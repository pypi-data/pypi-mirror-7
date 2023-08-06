from mock import MagicMock, patch
import pytest


def test_register_ansible_module_path():
    pass


def test_register_ansible_module_path_from_multiple_entry_points():
    pass


@pytest.fixture
def aws(awsconf):
    from mr.awsome import AWS
    import mr.awsome_ansible
    import mr.awsome.tests.dummy_plugin
    awsconf.fill([
        '[dummy-instance:foo]'])
    aws = AWS(configpath=awsconf.directory)
    aws.plugins = {
        'dummy': mr.awsome.tests.dummy_plugin.plugin,
        'ansible': mr.awsome_ansible.plugin}
    return aws


def test_configure_without_args(aws):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'configure'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: aws configure' in output
    assert 'too few arguments' in output


def test_configure_with_nonexisting_instance(aws):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'configure', 'bar'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: aws configure' in output
    assert "argument instance: invalid choice: 'bar'" in output


def test_configure_with_missing_yml(aws):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'configure', 'foo'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'usage: aws configure' in output
    assert "argument instance: invalid choice: 'foo'" in output


def test_configure_with_empty_yml(aws, tempdir):
    tempdir['foo.yml'].fill('')
    with patch('mr.awsome_ansible.log') as LogMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'configure', 'foo'])
    assert len(LogMock.error.call_args_list) == 1
    call_args = LogMock.error.call_args_list[0][0]
    assert 'parse error: playbooks must be formatted as a YAML list' in call_args[0]


def test_configure_asks_when_no_host_in_yml(aws, tempdir):
    yml = tempdir['foo.yml']
    yml.fill([
        '---',
        '- {}'])
    with patch('mr.awsome_ansible.yesno') as YesNoMock:
        YesNoMock.return_value = False
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'configure', 'foo'])
    assert len(YesNoMock.call_args_list) == 1
    call_args = YesNoMock.call_args_list[0][0]
    assert "Do you really want to apply '%s' to the host '%s'?" % (yml.path, 'foo') in call_args[0]


def test_configure(aws, monkeypatch, tempdir):
    tempdir['foo.yml'].fill([
        '---',
        '- hosts: foo'])
    runmock = MagicMock()
    monkeypatch.setattr("ansible.playbook.PlayBook.run", runmock)
    aws(['./bin/aws', 'configure', 'foo'])
    assert runmock.called


def test_configure_playbook_option(aws, awsconf, tempdir):
    import ansible.playbook
    yml = tempdir['bar.yml']
    yml.fill([
        '---',
        '- hosts: foo'])
    awsconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml.path])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        aws(['./bin/aws', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == yml.path


def test_configure_playbook_option_shadowing(aws, awsconf, caplog, tempdir):
    import ansible.playbook
    yml_foo = tempdir['foo.yml']
    yml_foo.fill('')
    yml_bar = tempdir['bar.yml']
    yml_bar.fill([
        '---',
        '- hosts: foo'])
    awsconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml_bar.path])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        aws(['./bin/aws', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == yml_bar.path
    assert [x.message for x in caplog.records()] == [
        "Instance 'foo' has the 'playbook' option set, but there is also a playbook at the default location '%s', which differs from '%s'." % (yml_foo.path, yml_bar.path),
        "Using playbook at '%s'." % yml_bar.path]


def test_configure_roles_option(aws, awsconf, tempdir):
    import ansible.playbook
    awsconf.fill([
        '[dummy-instance:foo]',
        'roles = ham egg'])
    with patch.object(ansible.playbook.PlayBook, "run", autospec=True) as runmock:
        aws(['./bin/aws', 'configure', 'foo'])
    assert runmock.called
    assert runmock.call_args[0][0].filename == "<dynamically generated from ['ham', 'egg']>"
    assert runmock.call_args[0][0].playbook == [{'hosts': ['foo'], 'user': 'root', 'roles': ['ham', 'egg']}]
    assert runmock.call_args[0][0].play_basedirs == [tempdir.directory]


def test_configure_roles_default_playbook_conflict(aws, awsconf, caplog, tempdir):
    yml = tempdir['foo.yml']
    yml.fill('')
    awsconf.fill([
        '[dummy-instance:foo]',
        'roles = ham egg'])
    with pytest.raises(SystemExit):
        aws(['./bin/aws', 'configure', 'foo'])
    assert [x.message for x in caplog.records()] == [
        "Using playbook at '%s'." % yml.path,
        "You can't use a playbook and the 'roles' options at the same time for instance 'foo'."]


def test_configure_roles_playbook_option_conflict(aws, awsconf, caplog, tempdir):
    yml = tempdir['bar.yml']
    yml.fill([
        '---',
        '- hosts: foo'])
    awsconf.fill([
        '[dummy-instance:foo]',
        'playbook = %s' % yml.path,
        'roles = ham egg'])
    with pytest.raises(SystemExit):
        aws(['./bin/aws', 'configure', 'foo'])
    assert [x.message for x in caplog.records()] == [
        "Using playbook at '%s'." % yml.path,
        "You can't use a playbook and the 'roles' options at the same time for instance 'foo'."]


def test_playbook_without_args(aws):
    with patch('sys.stderr') as StdErrMock:
        StdErrMock.encoding = 'utf-8'
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'playbook'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'Usage: aws playbook playbook.yml' in output


def test_playbook_with_nonexisting_playbook(aws):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'playbook', 'bar.yml'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert "the playbook: bar.yml could not be found" in output


def test_playbook_with_empty_yml(aws, tempdir):
    yml = tempdir['foo.yml']
    yml.fill('')
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'playbook', yml.path])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'parse error: playbooks must be formatted as a YAML list' in output


def test_playbook_asks_when_no_host_in_yml(aws, tempdir):
    yml = tempdir['foo.yml']
    yml.fill([
        '---',
        '- {}'])
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'playbook', yml.path])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert 'hosts declaration is required' in output


def test_playbook(aws, monkeypatch, tempdir):
    yml = tempdir['foo.yml']
    yml.fill([
        '---',
        '- hosts: foo'])
    runmock = MagicMock()
    monkeypatch.setattr("ansible.playbook.PlayBook.run", runmock)
    aws(['./bin/aws', 'playbook', yml.path])
    assert runmock.called


def test_ansible_without_args(aws):
    with patch('sys.stdout') as StdOutMock:
        StdOutMock.encoding = 'utf-8'
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'ansible'])
    output = "".join(x[0][0] for x in StdOutMock.write.call_args_list)
    assert 'Usage: aws ansible' in output


def test_ansible_with_nonexisting_instance(aws):
    with patch('sys.stderr') as StdErrMock:
        with pytest.raises(SystemExit):
            aws(['./bin/aws', 'ansible', 'bar'])
    output = "".join(x[0][0] for x in StdErrMock.write.call_args_list)
    assert "No hosts matched" in output


def test_ansible(aws, monkeypatch):
    runmock = MagicMock()
    monkeypatch.setattr("ansible.runner.Runner.run", runmock)
    runmock.return_value = dict(
        contacted=dict(),
        dark=[])
    aws(['./bin/aws', 'ansible', 'foo', '-a', 'ls'])
    assert runmock.called


def test_execnet_connection(aws, monkeypatch):
    import tempfile
    init_ssh_key_mock = MagicMock()
    init_ssh_key_mock.return_value = dict()
    monkeypatch.setattr(
        "mr.awsome.tests.dummy_plugin.Instance.init_ssh_key", init_ssh_key_mock)
    makegateway_mock = MagicMock()
    monkeypatch.setattr("execnet.makegateway", makegateway_mock)
    channel_mock = makegateway_mock().remote_exec()
    channel_mock.receive.side_effect = [
        (0, aws.configpath, ''),
        None,
        (0, '{}', '')]
    monkeypatch.setattr("sys.stdin", tempfile.TemporaryFile())
    aws(['./bin/aws', 'ansible', 'foo', '-a', 'ls'])
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
def test_execnet_ssh_spec(aws, awsconf, monkeypatch, ssh_info, expected):
    from mr.awsome_ansible.execnet_connection import Connection
    runner = MagicMock()
    aws.configfile = awsconf.path
    runner._awsome_aws = aws
    init_ssh_key_mock = MagicMock()
    init_ssh_key_mock.return_value = ssh_info
    monkeypatch.setattr("mr.awsome_ansible.execnet_connection.RPC_CACHE", {})
    monkeypatch.setattr(
        "mr.awsome.tests.dummy_plugin.Instance.init_ssh_key", init_ssh_key_mock)
    makegateway_mock = MagicMock()
    monkeypatch.setattr("execnet.makegateway", makegateway_mock)
    connection = Connection(runner, 'foo', 87, 'blubber', None, None)
    connection.connect()
    call, = makegateway_mock.call_args_list
    spec = call[0][0]
    assert spec.ssh.split() == expected
