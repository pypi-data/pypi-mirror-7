{% block base %}
[
{% if 'bootstrap' in phases %}
	{"operation": "postback", "percent": 45, "message": "Preparing initial OS image."},
{% block bootstrap %}
	{"operation": "runcmd", "chroot": false, "command": ["mkdir", "-p", "$chroot"]},
{% endblock %}
	{"operation": "postback", "percent": 55, "message": "Initial OS image has been installed."},
{% endif %}

{% if 'packages' in phases %}
	{"operation": "postback", "percent": 57, "message": "Installing custom packages."},
{% block packages %}
{% endblock %}
{% endif %}

{% if 'custom' in phases %}
	{"operation": "postback", "percent": 65, "message": "Making customizations."},
{% block custom %}
{% endblock %}
{% endif %}

{% if 'configure' in phases %}
	{"operation": "postback", "percent": 75, "message": "Configuring the OS image."},
{% block configure %}
	{"operation": "render_template", "template": "base/fstab.tmpl", "target": "/etc/fstab"},
{% endblock %}
{% endif %}

{% if 'xen-tweaks' in phases %}
	{"operation": "postback", "percent": 83, "message": "Tweaking the OS image for Xen VPS use."},
{% block xentweaks %}
	{"operation": "runcmd", "chroot": true, "command": ["sed", "-i", "s:tty1:hvc0:g", "/etc/inittab"]},
{% endblock %}
{% endif %}

{% if 'cleanup' in phases %}
	{"operation": "postback", "percent": 88, "message": "Cleaning up."},
{% block cleanup %}
{% endblock %}
{% endif %}
	{"operation": "noop"}
]
{% endblock %}
