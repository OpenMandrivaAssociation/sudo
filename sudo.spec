# use fakeroot -ba sudo.spec to build!
%define pre 0

%define build_71 0
%if %build_71
%define _sysconfdir /etc
%endif

Summary:	Allows command execution as root for specified users
Name:		sudo
Version:	1.6.9p4
Release:	%mkrel 1
Epoch:		1
License:	GPL
Group:		System/Base
URL:		http://www.sudo.ws/sudo
%if %pre
Source:		http://www.sudo.ws/sudo/dist/%name-%version%pre.tar.gz
Source1:	http://www.sudo.ws/sudo/dist/%name-%version%pre.tar.gz.sig
%else
Source:		http://www.sudo.ws/sudo/dist/%name-%version.tar.gz
Source1:	http://www.sudo.ws/sudo/dist/%name-%version.tar.gz.sig
Source2:	sudo.pamd
%endif
Patch1:         sudo-1.6.8_p9-nss_ldap.patch
BuildRequires:  pam-devel
BuildRequires:  openldap-devel
BuildRoot:	%_tmppath/%name-%version

%description
Sudo is a program designed to allow a sysadmin to give limited root
privileges to users and log root activity. The basic philosophy is
to give as few privileges as possible but still allow people to get
their work done.

%prep
%if %pre
%setup -q -n %name-%version%pre
%else
%setup -q -n %name-%version
%endif

%patch1 -p1 -b .nss_ldap

%build
%serverbuild
%configure --with-logging=both \
           --with-logpath=/var/log/sudo.log \
	   --with-editor=/bin/vi \
           --enable-log-host \
           --disable-log-wrap \
           --with-pam \
           --with-env-editor \
           --with-noexec=no \
           --with-ldap \
           --with-secure-path="/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin:/usr/local/sbin" \
           CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE"
%make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr

%if %build_71
make prefix=%{buildroot}/usr sysconfdir=%{buildroot}/etc \
 install_uid=$UID install_gid=$(id -g) sudoers=uid=$UID sudoers_gid=$(id -g) \
 install
make prefix=%{buildroot}/usr sysconfdir=%{buildroot}/etc \
 install_uid=$UID install_gid=$(id -g) sudoers=uid=$UID sudoers_gid=$(id -g) \
 install-sudoers
%else
%makeinstall \
install_uid=$UID install_gid=$(id -g) sudoers=uid=$UID sudoers_gid=$(id -g)
%endif

mkdir -p %{buildroot}/var/run/sudo
chmod 700 %{buildroot}/var/run/sudo

install -D -m644 %{SOURCE2} %{buildroot}/etc/pam.d/sudo

# Installing logrotated file
mkdir -p %{buildroot}/etc/logrotate.d
cat <<END >%{buildroot}/etc/logrotate.d/sudo
/var/log/sudo.log {
    missingok
    monthly
    compress
}
END
chmod 755 %{buildroot}/usr/bin/sudo
chmod 755 %{buildroot}/usr/sbin/visudo

install -m 755 sudoers2ldif %{buildroot}%{_bindir}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc BUGS CHANGES HISTORY INSTALL PORTING README README.LDAP TODO
%doc TROUBLESHOOTING UPGRADE sample.sudoers
%attr(0440,root,root) %config(noreplace) %{_sysconfdir}/sudoers
%config(noreplace) %{_sysconfdir}/logrotate.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo
%{_bindir}/sudoers2ldif
%attr(4111,root,root) %{_bindir}/sudo
%attr(4111,root,root) %{_bindir}/sudoedit
%attr(0111,root,root) %{_sbindir}/visudo
%{_mandir}/*/*
/var/run/sudo
