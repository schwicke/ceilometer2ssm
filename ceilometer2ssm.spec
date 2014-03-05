Summary: OpenStack Ceilometer to SSM2 interface
Name: ceilometer2ssm
Version: 0.2.0
Release: 1%{?dist}
License: ASL 2.0
Vendor: CERN, ASGC
Group: Applications/Internet
BuildArch: noarch
BuildRoot:  %{_tmppath}/%{name}
Url: https://github.com/schwicke/ceilometer2ssm
#Source0: %{name}.tar.gz
Source0: http://cern.ch/uschwick/software/ceilometer2ssm/%{version}/%{name}.tar.gz
BuildRequires: automake
BuildRequires: autoconf
Requires: apel-ssm
Requires: python-dirq


%description
provides an interface between APEL and OpenStack Ceilometer

%prep
%setup -q -n %{name}
./autogen.sh

%configure
%build
make
 
%install
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
make DESTDIR=%{buildroot} install

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-,root,root)
/usr/libexec/ceilometer2ssm
/usr/libexec/cloudaccounting
%config(noreplace) /etc/logrotate.d/ceilometer2ssm
%config(noreplace) /etc/cron.d/cloudaccounting.cron
%config(noreplace) /etc/ceilometer2ssm.conf
%doc /usr/share/doc/ceilometer2ssm/README

%changelog
* Mon Mar 5 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.2.0-1
- cern branch
- move back to pyCurl for keystone auth (due to issues with httplib)
- use keystone V3

* Mon Jan 21 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.1.4-1
- havana patches
- multiple bug fixes and code reshuffling

* Mon Oct 07 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.1.3-1
- merge with ASGC code
- code reshuffling
- add accounting group concept
- add code which dumps unfiltered ceilometer data for local displaing

* Fri Sep 13 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.1.2-2
- build patches only

* Fri Sep 13 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.1.2-1
- add log rotation
- introduce debugging flag

* Thu Sep 12 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.1.1-1
- add cron job to enable a daily upload

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.5-1
- APEL-cloud-message should appear only once 
- convert stuff read from config to ascii from unicode

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.3-1
- fix state

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.2-1
- omit fields if the values are not defined instead or reporting NULL
- more verbose output for debugging
- fix output format

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.1-1
- initial version

