%global __reqires_exclude_from %{_docdir}
%global __requires_exclude /usr/bin/perl|perl\\(.*)

Summary:	Allows command execution as root for specified users
Name:		sudo
Version:	1.9.7p2
Release:	1
License:	GPLv2+
Group:		System/Base
URL:		http://www.sudo.ws/sudo
Source0:	http://www.sudo.ws/sudo/dist/%{name}-%{version}.tar.gz
Source1:	%{name}.rpmlintrc
Source2:	sudo.pamd
Source3:	sudo-1.7.4p4-sudoers
Patch2:		sudo-1.7.2p1-envdebug.patch
BuildRequires:	autoconf-archive
BuildRequires:	bison
BuildRequires:	groff-for-man
BuildRequires:	pkgconfig(libcap)
BuildRequires:	openldap-devel
BuildRequires:	pam-devel

%description
Sudo (superuser do) allows a system administrator to give certain users (or
groups of users) the ability to run some (or all) commands as root while
logging all commands and arguments. Sudo operates on a per-command basis.
It is not a replacement for the shell. Features include: the ability to
restrict what commands a user may run on a per-host basis, copious logging
of each command (providing a clear audit trail of who did what), a
configurable timeout of the sudo command, and the ability to use the same
configuration file (sudoers) on many different machines.

%package devel
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{name} = %{EVRD}

%description devel
The %{name}-devel package contains header files developing sudo
plugins that use %{name}.

%prep
%autosetup -p1

# handle newer autoconf
autoreconf -fvi

# fix attribs and filenames
find -name "Makefile.*" | xargs sed -i -e "s|-m 0444|-m 0644|g;s|configure.in|configure.ac|g"

%build
%serverbuild
export CFLAGS="%{optflags} -Oz -D_GNU_SOURCE"

%configure \
	--without-rpath \
	--with-logging=both \
	--with-logfac=authpriv \
	--with-logpath=%{_logdir}/sudo.log \
	--with-editor=/bin/vi \
	--enable-log-host \
	--with-pam \
	--with-pam-login \
	--with-env-editor \
	--with-noexec=no \
	--without-linux-audit \
	--with-ignore-dot \
	--with-tty-tickets \
	--libexecdir=%{_libdir}/sudo \
	--with-plugindir=%{_libdir}/sudo \
	--with-noexec=%{_libdir}/sudo/sudo_noexec.so \
	--with-ldap \
	--with-ldap-conf-file=%{_sysconfdir}/ldap.conf \
	--with-secure-path="/sbin:%{_sbindir}:/bin:%{_bindir}:/usr/local/bin:/usr/local/sbin" \
	--with-passprompt="[sudo] password for %p: " \
	--with-sssd \
	--with-insults \
	--with-all-insults

%make_build

%install
install -d %{buildroot}/usr
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sudoers.d
install -d %{buildroot}%{_var}/db/sudo
install -d %{buildroot}%{_logdir}/sudo
install -d %{buildroot}%{_logdir}/sudo-io

%make_install install_uid=$(id -u) install_gid=$(id -g) sudoers_uid=$(id -u) sudoers_gid=$(id -g)

install -m0644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/pam.d/sudo
install -m0644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/sudoers
#install -m0755 plugins/sudoers/sudoers2ldif %{buildroot}%{_bindir}

# Installing logrotated file
cat <<END >%{buildroot}%{_sysconfdir}/logrotate.d/sudo
%{_logdir}/sudo.log {
    missingok
    monthly
    compress
}
END

cat > %{buildroot}%{_sysconfdir}/pam.d/sudo << EOF
#%%PAM-1.0
auth       include      system-auth
account    include      system-auth
password   include      system-auth
session    optional     pam_keyinit.so revoke
session    required     pam_limits.so
EOF

cat > %{buildroot}%{_sysconfdir}/pam.d/sudo-i << EOF
#%%PAM-1.0
auth       include      sudo
account    include      sudo
password   include      sudo
session    optional     pam_keyinit.so force revoke
session    required     pam_limits.so
EOF

# so that strip can touch it...
chmod 755 %{buildroot}%{_bindir}/*
chmod 755 %{buildroot}%{_sbindir}/*

# (tpg) create the missing log file
touch %{buildroot}%{_logdir}/sudo.log

# (tpg) get rid of huge ChangeLog file
rm -rf %{buildroot}%{_docdir}/sudo/ChangeLog

%find_lang sudo sudoers %{name}.lang

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%attr(0440,root,root) %config(noreplace) %{_sysconfdir}/sudoers
%attr(0440,root,root) %{_sysconfdir}/sudoers.dist
%attr(0750,root,root) %dir %{_sysconfdir}/sudoers.d/
%config(noreplace) %{_sysconfdir}/sudo.conf
%config(noreplace) %{_sysconfdir}/sudo_logsrvd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo-i
#%attr(0755,root,root) %{_bindir}/sudoers2ldif
%attr(4111,root,root) %{_bindir}/sudo
%{_bindir}/sudoedit
%{_bindir}/cvtsudoers
%attr(0111,root,root) %{_bindir}/sudoreplay
%attr(0755,root,root) %{_sbindir}/visudo
%ghost %{_logdir}/sudo.log
%{_sbindir}/sudo_logsrvd
%{_sbindir}/sudo_sendlog
%{_mandir}/man1/cvtsudoers.1*
%{_mandir}/man8/sudoreplay.8*
%{_mandir}/man8/visudo.8*
%{_mandir}/man8/sudoedit.8*
%{_mandir}/man8/sudo.8*
%{_mandir}/man8/sudo_logsrvd.8*
%{_mandir}/man8/sudo_sendlog.8*
%{_mandir}/man5/sudo.conf.5*
%{_mandir}/man5/sudoers.ldap.5*
%{_mandir}/man5/sudoers.5*
%{_mandir}/man5/sudoers_timestamp.5*
%{_mandir}/man5/sudo_logsrv.proto.5*
%{_mandir}/man5/sudo_logsrvd.conf.5*
%attr(0700,root,root) %dir %{_var}/db/sudo
%attr(0750,root,root) %dir %{_logdir}/sudo-io
%attr(0755,root,root) %dir %{_libdir}/sudo
%{_libdir}/sudo/*
%{_tmpfilesdir}/%{name}.conf

%files devel
%{_includedir}/sudo_plugin.h
%{_mandir}/man8/sudo_plugin.8*
