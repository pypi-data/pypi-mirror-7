{% extends "base.spec" %}
{% set possible_launch_cmds=['/sbin/start-stop-daemon', '/usr/sbin/invoke-rc.d'] %}
{% if not mirroruri %}
{% set mirroruri='http://mirrors.centarra.com/debian' %}
{% endif %}
{% block bootstrap %}
	{"operation": "runcmd", "chroot": false, "command": ["debootstrap", "--arch", "$debarch", "{{ distribution }}", "$chroot", "{{ mirroruri }}"]},
	{"operation": "setenv", "key": "LANG", "value": "C"},
	{% for command in possible_launch_cmds %}
		{"operation": "runcmd", "chroot": true, "command": ["mv", "{{ command }}", "{{ command }}.REAL"]},
		{"operation": "runcmd", "chroot": true, "command": ["ln", "-sf", "/bin/true", "{{ command }}"]},
	{% endfor %}
	{"operation": "setenv", "key": "DEBIAN_FRONTEND", "value": "noninteractive"},
	{"operation": "render_template", "template": "{{ distro_type | default('debian', true) }}/sources.tmpl", "target": "/etc/apt/sources.list", "distribution": "{{ distribution }}", "mirroruri": "{{ mirroruri }}"},
	{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "update"]},
	{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "openssh-server", "e2fsprogs"]},
	{% if distro_type != 'ubuntu' %}
		{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "locales"]},
	{% endif %}
	{% block kernelinst %}
		{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "linux-image-$debarch"]},
		{% if 'xen-tweaks' in phases %}
			{"operation": "render_template", "template": "debian/grub-menu.lst.tmpl", "target": "/boot/grub/menu.lst"},
		{% endif %}
	{% endblock %}
{% endblock %}
{% block packages %}
	{% for package in packages %}
		{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "{{ package }}"]},
	{% endfor %}
{% endblock %}
{% block configure %}
	{{ super() }}
	{"operation": "render_template", "template": "debian/interfaces.tmpl", "target": "/etc/network/interfaces"},
	{"operation": "render_template", "template": "debian/hostname.tmpl", "target": "/etc/hostname"},
	{"operation": "render_template", "template": "gentoo/locale-gen.tmpl", "target": "/etc/locale.gen"},
	{"operation": "runcmd", "chroot": true, "command": ["locale-gen"]},
{% endblock %}
{% block cleanup %}
	{"operation": "setenv", "key": "DEBIAN_FRONTEND", "value": null},
	{% for command in possible_launch_cmds %}
		{"operation": "runcmd", "chroot": true, "command": ["rm", "-f", "{{ command }}"]},
		{"operation": "runcmd", "chroot": true, "command": ["mv", "{{ command }}.REAL", "{{ command }}"]},
	{% endfor %}
{% endblock %}
