from mock import MagicMock, patch
import logging
import pytest


def test_register_ansible_module_path():
    pass


def test_register_ansible_module_path_from_multiple_entry_points():
    pass


@pytest.fixture
def ctrl(ployconf):
    from ploy import Controller
    import ploy_ansible
    import ploy.tests.dummy_plugin
    ployconf.fill([
        '[dummy-instance:foo]'])
    ctrl = Controller(configpath=ployconf.directory)
    ctrl.plugins = {
        'dummy': ploy.tests.dummy_plugin.plugin,
        'ansible': ploy_ansible.plugin}
    return ctrl


def caplog_messages(caplog, level=logging.INFO):
    return [
        x.message
        for x in caplog.records()
        if x.levelno >= level]


def test_configure_without_args(ctrl):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'configure'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: ploy configure' in output
    assert 'too few arguments' in output


def test_configure_with_nonexisting_instance(ctrl):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'configure', 'bar'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: ploy configure' in output
    assert "argument instance: invalid choice: 'bar'" in output


def test_configure_with_missing_yml(ctrl):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'configure', 'foo'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: ploy configure' in output
    assert "argument instance: invalid choice: 'foo'" in output


def test_configure_with_empty_yml(ctrl, tempdir):
    tempdir['default-foo.yml'].fill('')
    with patch('ploy_ansible.log') as LogMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'configure', 'foo'])
    assert len(LogMock.error.call_args_list) == 1
    call_args = LogMock.error.call_args_list[0][0]
    assert 'parse error: playbooks must be formatted as a YAML list' in call_args[0]


def test_configure_asks_when_no_host_in_yml(ctrl, tempdir):
    yml = tempdir['default-foo.yml']
    yml.fill([
        '---',
        '- {}'])
    with patch('ploy_ansible.yesno') as YesNoMock:
        YesNoMock.return_value = False
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'configure', 'foo'])
    assert len(YesNoMock.call_args_list) == 1
    call_args = YesNoMock.call_args_list[0][0]
    assert "Do you really want to apply '%s' to the host '%s'?" % (yml.path, 'default-foo') in call_args[0]


def test_configure(ctrl, monkeypatch, tempdir):
    tempdir['default-foo.yml'].fill([
        '---',
        '- hosts: default-foo'])
    runmock = MagicMock()
    monkeypatch.setattr("ansible.playbook.PlayBook.run", runmock)
    ctrl(['./bin/ploy', 'configure', 'foo'])
    assert runmock.called


def test_configure_playbook_option(ctrl, ployconf, tempdir):
    import ansible.playbook
    yml = tempdir['default-bar.yml']
    yml.fill([
        '---',
        '- hosts: default-foo'])
    ployconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml.path])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        ctrl(['./bin/ploy', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == yml.path


def test_configure_playbook_option_shadowing(ctrl, ployconf, caplog, tempdir):
    import ansible.playbook
    yml_foo = tempdir['default-foo.yml']
    yml_foo.fill('')
    yml_bar = tempdir['default-bar.yml']
    yml_bar.fill([
        '---',
        '- hosts: default-foo'])
    ployconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml_bar.path])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        ctrl(['./bin/ploy', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == yml_bar.path
    assert [x.message for x in caplog.records()] == [
        "Instance 'dummy-instance:foo' has the 'playbook' option set, but there is also a playbook at the default location '%s', which differs from '%s'." % (yml_foo.path, yml_bar.path),
        "Using playbook at '%s'." % yml_bar.path]


def test_configure_roles_option(ctrl, ployconf, tempdir):
    import ansible.playbook
    ployconf.fill([
        '[dummy-instance:foo]',
        'roles = ham egg'])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        ctrl(['./bin/ploy', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == "<dynamically generated from ['ham', 'egg']>"
    assert runmock.call_args[0][0].playbook == [{'hosts': ['default-foo'], 'user': 'root', 'roles': ['ham', 'egg']}]
    assert runmock.call_args[0][0].play_basedirs == [tempdir.directory]


def test_configure_roles_default_playbook_conflict(ctrl, ployconf, caplog, tempdir):
    yml = tempdir['default-foo.yml']
    yml.fill('')
    ployconf.fill([
        '[dummy-instance:foo]',
        'roles = ham egg'])
    with pytest.raises(SystemExit):
        ctrl(['./bin/ploy', 'configure', 'foo'])
    assert [x.message for x in caplog.records()] == [
        "Using playbook at '%s'." % yml.path,
        "You can't use a playbook and the 'roles' options at the same time for instance 'dummy-instance:foo'."]


def test_configure_roles_playbook_option_conflict(ctrl, ployconf, caplog, tempdir):
    yml = tempdir['default-bar.yml']
    yml.fill([
        '---',
        '- hosts: default-foo'])
    ployconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml.path,
        'roles = ham egg'])
    with pytest.raises(SystemExit):
        ctrl(['./bin/ploy', 'configure', 'foo'])
    assert [x.message for x in caplog.records()] == [
        "Using playbook at '%s'." % yml.path,
        "You can't use a playbook and the 'roles' options at the same time for instance 'dummy-instance:foo'."]


def test_playbook_without_args(ctrl):
    with patch('sys.stderr') as StdErrMock:
        StdErrMock.encoding = 'utf-8'
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'playbook'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'Usage: ploy playbook playbook.yml' in output


def test_playbook_with_nonexisting_playbook(ctrl):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'playbook', 'bar.yml'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert "the playbook: bar.yml could not be found" in output


def test_playbook_with_empty_yml(ctrl, tempdir):
    yml = tempdir['foo.yml']
    yml.fill('')
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'playbook', yml.path])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'parse error: playbooks must be formatted as a YAML list' in output


def test_playbook_asks_when_no_host_in_yml(ctrl, tempdir):
    yml = tempdir['foo.yml']
    yml.fill([
        '---',
        '- {}'])
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'playbook', yml.path])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'hosts declaration is required' in output


def test_playbook(ctrl, monkeypatch, tempdir):
    yml = tempdir['foo.yml']
    yml.fill([
        '---',
        '- hosts: foo'])
    runmock = MagicMock()
    monkeypatch.setattr("ansible.playbook.PlayBook.run", runmock)
    ctrl(['./bin/ploy', 'playbook', yml.path])
    assert runmock.called


def test_ansible_without_args(ctrl):
    with patch('sys.stdout') as StdOutMock:
        StdOutMock.encoding = 'utf-8'
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'ansible'])
    output = "".join(x[0][0] for x in StdOutMock.write.call_args_list)
    assert 'Usage: ploy ansible' in output


def test_ansible_with_nonexisting_instance(ctrl):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            ctrl(['./bin/ploy', 'ansible', 'bar'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert "No hosts matched" in output


def test_ansible(ctrl, monkeypatch):
    runmock = MagicMock()
    monkeypatch.setattr("ansible.runner.Runner.run", runmock)
    runmock.return_value = dict(
        contacted=dict(),
        dark=[])
    ctrl(['./bin/ploy', 'ansible', 'default-foo', '-a', 'ls'])
    assert runmock.called


def test_inventory_deprecation(caplog, ctrl, ployconf):
    from ploy_ansible.inventory import Inventory
    ctrl.configfile = ployconf.path
    ployconf.fill([
        '[dummy-instance:foo]',
        'test = 1'])
    inventory = Inventory(ctrl)
    variables = inventory.get_variables('default-foo')
    assert caplog_messages(caplog) == []
    assert variables['ploy_test']
    assert caplog_messages(caplog) == []
    assert variables['awsome_test']
    msg, = caplog_messages(caplog)
    lines = msg.splitlines()
    assert lines[0] == "Use of deprecated variable name 'awsome_test', use 'ploy_test' instead."
    parts = lines[1].rsplit(':', 1)
    assert parts[0].endswith("ploy_ansible/test_ansible.py")
    assert lines[2] == "    assert variables['awsome_test']"


def test_execnet_connection(ctrl, monkeypatch):
    import tempfile
    init_ssh_key_mock = MagicMock()
    init_ssh_key_mock.return_value = dict()
    monkeypatch.setattr(
        "ploy.tests.dummy_plugin.Instance.init_ssh_key", init_ssh_key_mock)
    makegateway_mock = MagicMock()
    monkeypatch.setattr("execnet.makegateway", makegateway_mock)
    channel_mock = makegateway_mock().remote_exec()
    channel_mock.receive.side_effect = [
        (0, ctrl.configpath, ''),
        None,
        (0, '{}', '')]
    monkeypatch.setattr("sys.stdin", tempfile.TemporaryFile())
    ctrl(['./bin/ploy', 'ansible', 'default-foo', '-a', 'ls'])
    assert [x[0][0][0] for x in channel_mock.send.call_args_list] == [
        'exec_command', 'put_file', 'exec_command']
    assert [x[0][0][2] for x in channel_mock.send.call_args_list] == [
        {}, {}, {}]
    assert 'mkdir' in channel_mock.send.call_args_list[0][0][0][1][0]
    assert 'CommandModule' in channel_mock.send.call_args_list[1][0][0][1][0]


@pytest.mark.parametrize("ssh_info, expected", [
    (dict(host='foo'), ['foo']),
    (dict(host='foo', port=22), ['-p', '22', 'foo']),
    (dict(host='foo', port=22, ProxyCommand='ssh master -W 10.0.0.1'),
     ['-o', 'ProxyCommand=ssh master -W 10.0.0.1', '-p', '22', 'foo'])])
def test_execnet_ssh_spec(ctrl, ployconf, monkeypatch, ssh_info, expected):
    from ploy_ansible.execnet_connection import Connection
    runner = MagicMock()
    ctrl.configfile = ployconf.path
    runner._ploy_ctrl = ctrl
    init_ssh_key_mock = MagicMock()
    init_ssh_key_mock.return_value = ssh_info
    monkeypatch.setattr("ploy_ansible.execnet_connection.RPC_CACHE", {})
    monkeypatch.setattr(
        "ploy.tests.dummy_plugin.Instance.init_ssh_key", init_ssh_key_mock)
    makegateway_mock = MagicMock()
    monkeypatch.setattr("execnet.makegateway", makegateway_mock)
    connection = Connection(runner, 'foo', 87, 'blubber', None, None)
    connection.connect()
    call, = makegateway_mock.call_args_list
    spec = call[0][0]
    assert spec.ssh.split() == expected
