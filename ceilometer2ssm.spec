Summary: OpenStack Ceilometer to SSM2 interface
Name: ceilometer2ssm
Version: 0.1.2
Release: 2%{?dist}
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

