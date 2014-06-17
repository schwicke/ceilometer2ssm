%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif
Summary: OpenStack Ceilometer to SSM2 interface
Name: ceilometer2ssm
Version: 0.3.1
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
BuildRequires: python-devel
BuildRequires: python-setuptools
Requires: apel-ssm
Requires: python-dirq
Requires: python-sqlalchemy0.7
Requires: python-suds
Requires: python-pycurl
Requires: python-httplib2

%description
provides an interface between APEL and OpenStack Ceilometer

%prep
%setup -q -n %{name}

%configure
%build
(cd cloudaccounting && %{__python} setup.py build)
make
 
%install
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
(cd cloudaccounting && %{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT --install-lib %{python2_sitearch})
make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}/var/lib/ceilodata
chmod 0750 %{buildroot}/var/lib/ceilodata
mkdir -p %{buildroot}/var/log/ceilodata
chmod 0750 %{buildroot}/var/log/ceilodata

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-,root,root)

%{python2_sitearch}
%{_bindir}

%config(noreplace) /etc/logrotate.d/ceilometer2ssm
%config(noreplace) /etc/ceilometer2ssm.conf
%config(noreplace) /etc/ceilodata.conf
%doc /usr/share/doc/ceilometer2ssm
%dir /var/lib/ceilodata
%dir /var/log/ceilodata

%changelog
* Mon Jun 16 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.3.1-2
- add sample for ceilodatastore cron 
- backward compatibility fixings

* Fri Jun 13 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.3.0-1
- split ceilometer2ssm into different pieces
- use shadow database to flatten results
- add tool to do the publication from the cache database

* Fri Mar 14 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.2.2-1
- bug fix release and cleanup

* Mon Mar 5 2014 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.2.1-1
- cern branch
- move back to pyCurl for keystone auth (due to issues with httplib)
- use keystone V3
- loop over each project and re-auth before querying ceilometer

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

