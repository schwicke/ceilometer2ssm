Summary: ceilomter to SSM2 interface
Name: ceilometer2ssm
Version: 0.0.4
Release: 1%{?dist}
License: ASL2
Group: PES
Vendor: CERN, ASGC
BuildArch: noarch
BuildRoot:  %{_tmppath}/%{name}
Source0: %{name}.tar.gz
BuildRequires: automake
BuildRequires: autoconf
Requires: apel-ssm
Requires: python-dirq


%description
provides an interface between APEL and ceilometer

%prep
%setup -n %{name}

%build
./autogen.sh
./configure --prefix=$RPM_BUILD_ROOT
make
 
%install
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
make install

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-,root,root)
/usr/libexec/ceilometer2ssm
%config(noreplace) /etc/ceilometer2ssm.conf

%post 

%preun

%changelog

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.4-1
- APEL-cloud-message should appear only once 

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.3-1
- fix state

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.2-1
- omit fields if the values are not defined instead or reporting NULL
- more verbose output for debugging
- fix output format

* Wed Sep 11 2013 Ulrich Schwickerath <Ulrich.Schwickerath@cern.ch> -0.0.1-1
- initial version

