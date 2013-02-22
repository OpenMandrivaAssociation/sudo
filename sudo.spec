# use fakeroot -ba sudo.spec to build!
%define plevel p6

Summary:	Allows command execution as root for specified users
Name:		sudo
Version:	1.8.6%{?plevel}
Release:	1
Epoch:		1
License:	GPLv2+
Group:		System/Base
URL:		http://www.sudo.ws/sudo
Source0:	http://www.sudo.ws/sudo/dist/%{name}-%{version}.tar.gz
Source1:	http://www.sudo.ws/sudo/dist/%{name}-%{version}.tar.gz.sig
Source2:	sudo.pamd
Source3:	sudo-1.7.4p4-sudoers
Patch1:		sudo-1.6.7p5-strip.patch
Patch2:		sudo-1.7.2p1-envdebug.patch
Patch3:		sudo-1.8.6-m4path.patch
Patch4:		sudo-1.8.5-pipelist.patch
BuildRequires:	audit-devel
BuildRequires:	bison
BuildRequires:	groff-for-man
BuildRequires:	cap-devel
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

%package	devel
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{name} = %{version}-%{release}

%description	devel
The %{name}-devel package contains header files developing sudo
plugins that use %{name}.

%prep
%setup -q
%patch1 -p1 -b .strip~
%patch2 -p1 -b .envdebug~
%patch3 -p1 -b .m4path~
%patch4 -p1 -b .pipelist~
# handle newer autoconf
mv aclocal.m4 acinclude.m4
autoreconf -fvi

# fix attribs
find -name "Makefile.*" | xargs perl -pi -e "s|-m 0444|-m 0644|g"

%build
%serverbuild
export CFLAGS="%{optflags} -D_GNU_SOURCE"

%configure2_5x \
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
	--with-linux-audit \
	--with-ignore-dot \
	--with-tty-tickets \
	--libexecdir=%{_libdir}/sudo \
	--with-plugindir=%{_libdir}/sudo \
	--with-noexec=%{_libdir}/sudo/sudo_noexec.so \
	--with-ldap \
	--with-ldap-conf-file=%{_sysconfdir}/ldap.conf \
	--with-secure-path="/sbin:%{_sbindir}:/bin:%{_bindir}:/usr/local/bin:/usr/local/sbin" \
	--with-passprompt="[sudo] password for %p: " \
	--with-sssd

%make

%install
install -d %{buildroot}/usr
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sudoers.d
install -d %{buildroot}%{_var}/db/sudo
install -d %{buildroot}%{_logdir}/sudo
install -d %{buildroot}%{_logdir}/sudo-io

%makeinstall_std install_uid=`id -u` install_gid=`id -g` sudoers_uid=`id -u` sudoers_gid=`id -g`

install -m0644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/pam.d/sudo
install -m0644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/sudoers
install -m0755 plugins/sudoers/sudoers2ldif %{buildroot}%{_bindir}

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

%find_lang sudo sudoers %{name}.lang

%post
/bin/chmod 0440 %{_sysconfdir}/sudoers || :
%create_ghostfile %{_logdir}/sudo.log root root 600

%files -f %{name}.lang
%doc doc/LICENSE doc/HISTORY README README.LDAP
%doc doc/TROUBLESHOOTING doc/UPGRADE doc/sample.* doc/schema.*
%attr(0440,root,root) %config(noreplace) %{_sysconfdir}/sudoers
%attr(0750,root,root) %dir %{_sysconfdir}/sudoers.d/
%config(noreplace) %{_sysconfdir}/logrotate.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo-i
%attr(0755,root,root) %{_bindir}/sudoers2ldif
%attr(4111,root,root) %{_bindir}/sudo
%attr(4111,root,root) %{_bindir}/sudoedit
%attr(0111,root,root) %{_bindir}/sudoreplay
%attr(0755,root,root) %{_sbindir}/visudo
%ghost %{_logdir}/sudo.log
%{_mandir}/man8/sudoreplay.8*
%{_mandir}/man8/visudo.8*
%{_mandir}/man8/sudoedit.8*
%{_mandir}/man8/sudo.8*
%{_mandir}/man5/sudoers.ldap.5*
%{_mandir}/man5/sudoers.5*

%attr(0700,root,root) %dir %{_var}/db/sudo
%attr(0750,root,root) %dir %{_logdir}/sudo-io
%attr(0755,root,root) %dir %{_libdir}/sudo
%{_libdir}/sudo/sudo_noexec.so
%{_libdir}/sudo/sudoers.so

%files devel
%doc plugins/{sample,sample_group}
%{_includedir}/sudo_plugin.h
%{_mandir}/man8/sudo_plugin.8*
