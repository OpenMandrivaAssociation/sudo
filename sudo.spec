# use fakeroot -ba sudo.spec to build!
%define plevel p2

Summary:	Allows command execution as root for specified users
Name:		sudo
Version:	1.7.6%{?plevel}
Release:	1
Epoch:		1
License:	GPLv2+
Group:		System/Base
URL:		http://www.sudo.ws/sudo
Source0:	http://www.sudo.ws/sudo/dist/%name-%version.tar.gz
Source1:	http://www.sudo.ws/sudo/dist/%name-%version.tar.gz.sig
Source2:	sudo.pamd
Source3:	sudo-1.7.4p4-sudoers
Patch1:		sudo-1.6.7p5-strip.patch
Patch2:		sudo-1.7.2p1-envdebug.patch
Patch3:		sudo-1.7.4p3-m4path.patch
BuildRequires:	audit-devel
BuildRequires:	bison
BuildRequires:	groff-for-man
BuildRequires:	libcap-devel
BuildRequires:	openldap-devel
BuildRequires:	pam-devel
Requires(pre):	openldap
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Sudo is a program designed to allow a sysadmin to give limited root
privileges to users and log root activity. The basic philosophy is
to give as few privileges as possible but still allow people to get
their work done.

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1 -b .strip
%patch2 -p1 -b .envdebug
%patch3 -p1 -b .m4path

%build
# handle newer autoconf
rm -f acsite.m4
mv aclocal.m4 acinclude.m4
autoreconf -fv --install

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
	--with-ldap \
	--with-ldap-conf-file=%{_sysconfdir}/ldap.conf \
	--with-secure-path="/sbin:%{_sbindir}:/bin:%{_bindir}:/usr/local/bin:/usr/local/sbin" \
	--with-passprompt="[sudo] password for %p: "

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}/usr
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sudoers.d
install -d %{buildroot}%{_sysconfdir}/pam.d
install -d %{buildroot}%{_var}/db/sudo
install -d %{buildroot}%{_logdir}/sudo
install -d %{buildroot}%{_logdir}/sudo-io

%makeinstall_std install_uid=$UID install_gid=$(id -g) sudoers=uid=$UID sudoers_gid=$(id -g)

install -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/sudo
install -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers
install -m0755 sudoers2ldif %{buildroot}%{_bindir}

# Installing logrotated file
cat <<END >%{buildroot}%{_sysconfdir}/logrotate.d/sudo
%{_logdir}/sudo.log {
    missingok
    monthly
    compress
}
END

cat > %{buildroot}%{_sysconfdir}/pam.d/sudo << EOF
#%PAM-1.0
auth       include      system-auth
account    include      system-auth
password   include      system-auth
session    optional     pam_keyinit.so revoke
session    required     pam_limits.so
EOF

cat > %{buildroot}%{_sysconfdir}/pam.d/sudo-i << EOF
#%PAM-1.0
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

%post
/bin/chmod 0440 %{_sysconfdir}/sudoers || :
%create_ghostfile %{_logdir}/sudo.log root root 600

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc HISTORY PORTING README README.LDAP
%doc TROUBLESHOOTING UPGRADE sample.sudoers
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
%{_mandir}/*/*
%attr(0700,root,root) %dir %{_var}/db/sudo
%attr(0750,root,root) %dir %{_logdir}/sudo-io
