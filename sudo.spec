# use fakeroot -ba sudo.spec to build!
%define pre p4

%define build_71 0
%if %build_71
%define _sysconfdir /etc
%endif

Name:		sudo
Version:	1.7.4
Release:	%mkrel 2.%{?pre}.1
Epoch:		1
Summary:	Allows command execution as root for specified users
License:	GPLv2+
Group:		System/Base
URL:		http://www.sudo.ws/sudo
Source0:	http://www.sudo.ws/sudo/dist/%name-%version%{?pre}.tar.gz
Source1:	http://www.sudo.ws/sudo/dist/%name-%version%{?pre}.tar.gz.sig
Source2:	sudo.pamd
BuildRequires:	pam-devel
BuildRequires:	openldap-devel
BuildRequires:	bison
BuildRequires:	groff-for-man
Requires(pre):	openldap
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
Sudo is a program designed to allow a sysadmin to give limited root
privileges to users and log root activity. The basic philosophy is
to give as few privileges as possible but still allow people to get
their work done.

%prep
%setup -q -n %{name}-%{version}%{?pre}

%build
%serverbuild
export CFLAGS="%{optflags} -D_GNU_SOURCE"

%configure2_5x \
	--without-rpath \
	--with-logging=both \
	--with-logpath=%{_logdir}/sudo.log \
	--with-editor=/bin/vi \
	--enable-log-host \
	--with-pam \
	--with-env-editor \
	--with-noexec=no \
	--with-ldap \
	--with-ldap-conf-file=%{_sysconfdir}/ldap.conf \
	--with-secure-path="/sbin:%{_sbindir}:/bin:%{_bindir}:/usr/local/bin:/usr/local/sbin"

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
%makeinstall_std \
install_uid=$UID install_gid=$(id -g) sudoers=uid=$UID sudoers_gid=$(id -g)
%endif

mkdir -p %{buildroot}%{_var}/run/sudo
chmod 700 %{buildroot}%{_var}/run/sudo

install -D -m644 %{SOURCE2} %{buildroot}/etc/pam.d/sudo

# Installing logrotated file
mkdir -p %{buildroot}/etc/logrotate.d
cat <<END >%{buildroot}/etc/logrotate.d/sudo
%{_logdir}/sudo.log {
    missingok
    monthly
    compress
}
END
chmod 755 %{buildroot}%{_bindir}/sudo
chmod 755 %{buildroot}%{_sbindir}/visudo

install -m 755 sudoers2ldif %{buildroot}%{_bindir}

# (tpg) create the missing log file
mkdir -p %{buildroot}%{_logdir}
touch %{buildroot}%{_logdir}/sudo.log

mkdir -p %{buildroot}/etc/sudoers.d/

%post
%create_ghostfile %{_logdir}/sudo.log root root 600

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc HISTORY PORTING README README.LDAP
%doc TROUBLESHOOTING UPGRADE sample.sudoers
%attr(0440,root,root) %config(noreplace) %{_sysconfdir}/sudoers
%dir %{_sysconfdir}/sudoers.d/
%config(noreplace) %{_sysconfdir}/logrotate.d/sudo
%config(noreplace) %{_sysconfdir}/pam.d/sudo
%{_bindir}/sudoers2ldif
%attr(4111,root,root) %{_bindir}/sudo
%attr(4111,root,root) %{_bindir}/sudoreplay
%attr(4111,root,root) %{_bindir}/sudoedit
%attr(0111,root,root) %{_sbindir}/visudo
%ghost %{_logdir}/sudo.log
%{_mandir}/*/*
%{_var}/run/sudo
