SUBDIRS = config src doc
PKGNAME = ceilometer2ssm
rpmtopdir = $(shell rpm --eval %_topdir)
RPMSOURCES = $(rpmtopdir)/SOURCES

rpm:	clean
	make -f Makefile.koji
	if [ "x$(RPM_MACROS)" != "x" ] ; then rpmbuild  --define "$(RPM_MACROS)"  -tb $(PKGNAME).tar.gz ; else rpmbuild -tb $(PKGNAME).tar.gz  ; fi
	rm -f /tmp/$(PKGNAME).tar.gz

srpm:	clean
	make -f Makefile.koji
	if [ "x$(RPM_MACROS)" != "x" ]; then rpmbuild --define "$(RPM_MACROS)"  -ts  $(PKGNAME).tar.gz ; else rpmbuild --nodeps -ts  $(PKGNAME).tar.gz ; fi
	rm -f $(RPMSOURCES)/$(PKGNAME).tar.gz 

ai5:	clean
	make -f Makefile.koji
	rpmbuild --define "dist .ai5"  -ts  $(PKGNAME).tar.gz 
	rm -f $(RPMSOURCES)/$(PKGNAME).tar.gz 

ai6:	clean
	make -f Makefile.koji
	rpmbuild --define "dist .ai6"  -ts  $(PKGNAME).tar.gz 
	rm -f $(RPMSOURCES)/$(PKGNAME).tar.gz 

sources: srpm

disclean: clean
	find . -name Makefile -exec rm -f \{} \;
	find . -name *~ -exec rm -f \{} \;
	rm -f missing  install-sh  config.log configure config.status 
