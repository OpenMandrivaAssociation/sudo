# use fakeroot -ba sudo.spec to build!
%define plevel p2

Summary:	Allows command execution as root for specified users
Name:		sudo
Version:	1.7.6%{?plevel}
Release:	2
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


%changelog
* Wed Jul 06 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.7.6p2-1
+ Revision: 688936
- new version
- drop P4 & P5 (fixed upstream)

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.4p6-3
+ Revision: 670223
- mass rebuild

* Sun Feb 27 2011 Funda Wang <fwang@mandriva.org> 1:1.7.4p6-2
+ Revision: 640255
- rebuild to obsolete old packages

* Fri Jan 21 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.4p6-1
+ Revision: 631998
- 1.7.4p6
- 1.7.4p5 (sync with sudo-1.7.4p5-2.fc15.src.rpm)
- add back the "p5" in the version string

* Sat Jan 15 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.4-2.p4.3
+ Revision: 631102
- fix CVE-2011-0008

* Wed Nov 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.4-2.p4.2mdv2011.0
+ Revision: 592998
- sync changes with fc15
- nuke old cruft

* Sun Sep 12 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.4-2.p4.1mdv2011.0
+ Revision: 577607
- 1.7.4p4

* Sun Aug 08 2010 Michael Scherer <misc@mandriva.org> 1:1.7.4-2mdv2011.0
+ Revision: 567715
- fix run with default config file, since /etc/sudoers.d is needed

* Tue Aug 03 2010 Funda Wang <fwang@mandriva.org> 1:1.7.4-1mdv2011.0
+ Revision: 565214
- new version 1.7.4

* Sat Jul 17 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.7.3-1mdv2011.0
+ Revision: 554564
- update to new version 1.7.3
- update file list

* Fri Jun 11 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.2-0.p7.1mdv2010.1
+ Revision: 547897
- 1.7.2p7

* Tue Apr 13 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.2-0.p6.1mdv2010.1
+ Revision: 534258
- 1.7.2p6

* Wed Feb 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.7.2-0.p4.1mdv2010.1
+ Revision: 510689
- 1.7.2p4

* Sun Aug 09 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.7.2-0.p1.1mdv2010.0
+ Revision: 412992
- update to new version 1.7.2p1

* Sat May 09 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.7.1-1mdv2010.0
+ Revision: 373790
- update to new version 1.7.1

* Thu May 07 2009 Colin Guthrie <cguthrie@mandriva.org> 1:1.7.0-2mdv2010.0
+ Revision: 372838
- Fix path to ldap.conf (do not use the openldap ldap.conf)

* Sat Dec 20 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.7.0-1mdv2009.1
+ Revision: 316503
- drop patch1
- set explicit path to the LDAP configuration file
- fix docs
- add openldap as a requires(pre)
- update to new version 1.7.0

* Fri Nov 14 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p18-1mdv2009.1
+ Revision: 303345
- update to new patch release 18

* Tue Aug 19 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p17-1mdv2009.0
+ Revision: 274076
- update to new patchlevel 17

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 1:1.6.9p16-3mdv2009.0
+ Revision: 265743
- rebuild early 2009.0 package (before pixel changes)

* Sun May 18 2008 Gustavo De Nardin <gustavodn@mandriva.com> 1:1.6.9p16-2mdv2009.0
+ Revision: 208578
- increase mkrel, and release

* Mon May 12 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p16-1mdv2009.0
+ Revision: 206501
- update to the latest patchlevel
- add missing log file

* Thu Apr 17 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p15-1mdv2009.0
+ Revision: 195280
- update to the latest patchlevel

* Thu Feb 21 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p13-1mdv2008.1
+ Revision: 173446
- update to the latest patchlevel
- add missing buildrequires on bison and groff-for-man

* Thu Jan 24 2008 Oden Eriksson <oeriksson@mandriva.com> 1:1.6.9p12-3mdv2008.1
+ Revision: 157335
- rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild with fixed %%serverbuild macro

* Tue Jan 22 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p12-1mdv2008.1
+ Revision: 155998
- new patch release

* Tue Jan 08 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p11-1mdv2008.1
+ Revision: 146899
- new patch release
- do not package INSTALL file

* Sat Dec 29 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p10-1mdv2008.1
+ Revision: 139063
- new patch release

* Fri Dec 21 2007 Oden Eriksson <oeriksson@mandriva.com> 1:1.6.9p8-3mdv2008.1
+ Revision: 136100
- rebuilt against openldap-2.4.7 libs

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Nov 06 2007 Olivier Thauvin <nanardon@mandriva.org> 1:1.6.9p8-2mdv2008.1
+ Revision: 106359
- rebuild for lzma man page

* Sat Nov 03 2007 Olivier Thauvin <nanardon@mandriva.org> 1:1.6.9p8-1mdv2008.1
+ Revision: 105508
- 1.6.9p8

* Fri Oct 26 2007 David Walluck <walluck@mandriva.org> 1:1.6.9p7-1mdv2008.1
+ Revision: 102443
- 1.6.9p7
- always include sudo.pamd in src.rpm
- call %%{configure2_5x}
- use correct macros for paths
- use standard buildroot

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - new release

* Thu Sep 13 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 1:1.6.9p5-1mdv2008.0
+ Revision: 85183
- Upstream's TODO file doesn't exist anymore.

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - new version

* Sat Aug 18 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p4-1mdv2008.0
+ Revision: 65404
- new version
- correct url

* Fri Aug 03 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p3-1mdv2008.0
+ Revision: 58394
- new version

* Thu Aug 02 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p2-1mdv2008.0
+ Revision: 57903
- new version
- remove /usr/X11R6/bin from the secure path

* Fri Jul 27 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9p1-2mdv2008.0
+ Revision: 56323
- new version (bugfixes)

* Mon Jul 23 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.6.9-2mdv2008.0
+ Revision: 54662
- %%{optflags} doesn't include the security flags set by %%serverbuild

* Sun Jul 22 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.6.9-1mdv2008.0
+ Revision: 54403
- remove patch 0
- new version

* Wed Jun 27 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.6.8p12-8mdv2008.0
+ Revision: 45062
- using new serverbuild macro (-fstack-protector)

* Fri Jun 22 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.6.8p12-7mdv2008.0
+ Revision: 43263
- use -fstack-protector


* Tue Feb 27 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.6.8p12-6mdv2007.0
+ Revision: 126251
- no ugly and unjustified file requires on /etc/pam.d/system-auth
- spec cleanup
- use patch from gentoo to fix nss issue (fix #23421)

* Fri Feb 23 2007 Thierry Vignaud <tvignaud@mandriva.com> 1:1.6.8p12-5mdv2007.1
+ Revision: 125075
- Import sudo

* Fri Feb 23 2007 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.6.8p12-5mdv2007.1
- update patch 0: whitelist GP_LANG & GP_LANGUAGE (#25419)

* Fri Sep 01 2006 Warly <warly@mandriva.com> 1:1.6.8p12-4mdv2007.0
- make sudo use a whitelist rather than blacklist

* Tue May 02 2006 Stefan van der Eijk <stefan@eijk.nu> 1:1.6.8p12-3mdk
- rebuild for sparc

* Tue Jan 31 2006 Olivier Blin <oblin@mandriva.com> 1.6.8p12-2mdk
- use "include" directive instead of deprecated pam_stack module
  (and remove hardcoded library path)
- move pam.d config in Source2

* Thu Dec 22 2005 Oden Eriksson <oeriksson@mandriva.com> 1.6.8p12-1mdk
- 1.6.8p12
- merged bits from the sudo-1.6.8p8-CVE-2005-2959_4158.patch

* Thu Oct 06 2005 Pascal Terjan <pterjan@mandriva.org> 1.6.8p9-1mdk
- 1.6.8p9

* Wed Aug 31 2005 Oden Eriksson <oeriksson@mandriva.com> 1.6.8p8-2mdk
- rebuilt against new openldap-2.3.6 libs

* Mon Jun 06 2005 Pascal TErjan <pterjan@mandriva.org> 1:1.6.8p8-1mdk
- 1.6.8p8
- summary-ended-with-dot

* Fri Feb 04 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.6.8p1-2mdk
- rebuild for ldap2.2_7

* Wed Sep 22 2004 Olivier Blin <blino@mandrake.org> 1.6.8p1-1mdk
- 1.6.8p1

* Sun Aug 29 2004 Olivier Blin <blino@mandrake.org> 1.6.8-2mdk
- ldap support
- add README.ldap and sudoers2ldif in package

* Sat Aug 28 2004 Olivier Blin <blino@mandrake.org> 1.6.8-1mdk
- 1.6.8
- spec file fixes for stable versions
- do not build sudo_noexec
- ship sudoedit

* Tue Aug 03 2004 Olivier Blin <blino@mandrake.org> 1.6.7-0.p5.3mdk
- define a sane secure path (fix bug 448)

