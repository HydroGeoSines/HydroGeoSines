!     -*- f90 -*-
!     This file is autogenerated with f2py (version:2)
!     It contains Fortran 90 wrappers to fortran functions.

      
      subroutine f2pyinitparams(f2pysetupfunc)
      use params, only : nullfile
      use params, only : pathsep
      use params, only : stdin
      use params, only : stdout
      use params, only : stderr
      use params, only : void
      use params, only : scr
      use params, only : ic2
      use params, only : comdir
      use params, only : cfprn
      use params, only : cfout
      use params, only : etddtdat
      use params, only : etpolutdat
      use params, only : etpolutbin
      use params, only : dpi
      use params, only : dpi2
      use params, only : drad
      use params, only : dro
      use params, only : cmodel
      use params, only : cffile
      use params, only : cufile
      use params, only : cunit
      use params, only : channel
      use params, only : compon
      use params, only : c88
      use params, only : c99
      use params, only : cendt
      external f2pysetupfunc
      call f2pysetupfunc(nullfile,pathsep,stdin,stdout,stderr,void,scr,i&
     &c2,comdir,cfprn,cfout,etddtdat,etpolutdat,etpolutbin,dpi,dpi2,drad&
     &,dro,cmodel,cffile,cufile,cunit,channel,compon,c88,c99,cendt)
      end subroutine f2pyinitparams

      
      subroutine f2pyinitmax_pars(f2pysetupfunc)
      use max_pars, only : maxwg
      use max_pars, only : maxnw
      external f2pysetupfunc
      call f2pysetupfunc(maxwg,maxnw)
      end subroutine f2pyinitmax_pars

      
      subroutine f2pyinitddt_mod(f2pysetupfunc)
      use ddt_mod, only : ddttab
      use ddt_mod, only : nddtab
      external f2pysetupfunc
      call f2pysetupfunc(ddttab,nddtab)
      end subroutine f2pyinitddt_mod

      
      subroutine f2pyinitcontrolmod(f2pysetupfunc)
      use controlmod, only : ngr
      use controlmod, only : dfra
      use controlmod, only : dfre
      use controlmod, only : dg0
      use controlmod, only : dphi0
      use controlmod, only : na
      use controlmod, only : ne
      use controlmod, only : dam
      use controlmod, only : dbod
      use controlmod, only : dlat
      use controlmod, only : dlon
      use controlmod, only : dh
      use controlmod, only : dgrav
      use controlmod, only : daz
      use controlmod, only : datlim
      use controlmod, only : damin
      use controlmod, only : dpoltc
      use controlmod, only : dlodtc
      use controlmod, only : idtsec
      use controlmod, only : cinst
      use controlmod, only : chead
      use controlmod, only : ic
      use controlmod, only : ir
      use controlmod, only : ity
      use controlmod, only : itm
      use controlmod, only : itd
      use controlmod, only : ith
      use controlmod, only : ida
      use controlmod, only : imodel
      use controlmod, only : iprobs
      use controlmod, only : ispanh
      use controlmod, only : kfilt
      use controlmod, only : iprlf
      use controlmod, only : irigid
      use controlmod, only : ihann
      use controlmod, only : iquick
      use controlmod, only : nf
      external f2pysetupfunc
      call f2pysetupfunc(ngr,dfra,dfre,dg0,dphi0,na,ne,dam,dbod,dlat,dlo&
     &n,dh,dgrav,daz,datlim,damin,dpoltc,dlodtc,idtsec,cinst,chead,ic,ir&
     &,ity,itm,itd,ith,ida,imodel,iprobs,ispanh,kfilt,iprlf,irigid,ihann&
     &,iquick,nf)
      end subroutine f2pyinitcontrolmod

      
      subroutine f2pyinittidphas(f2pysetupfunc)
      use tidphas, only : dpk
      external f2pysetupfunc
      call f2pysetupfunc(dpk)
      end subroutine f2pyinittidphas

      
      subroutine f2pyinittidwave(f2pysetupfunc)
      use tidwave, only : nw
      use tidwave, only : iwnr
      use tidwave, only : iaarg
      use tidwave, only : dx0
      use tidwave, only : dx1
      use tidwave, only : dx2
      use tidwave, only : dy0
      use tidwave, only : dy1
      use tidwave, only : dy2
      use tidwave, only : dthph
      use tidwave, only : dthfr
      use tidwave, only : dbody
      use tidwave, only : dc0
      use tidwave, only : ds0
      use tidwave, only : ddc
      use tidwave, only : dds
      external f2pysetupfunc
      call f2pysetupfunc(nw,iwnr,iaarg,dx0,dx1,dx2,dy0,dy1,dy2,dthph,dth&
     &fr,dbody,dc0,ds0,ddc,dds)
      end subroutine f2pyinittidwave

      
      subroutine f2pyinitlove(f2pysetupfunc)
      use love, only : dglat
      use love, only : dhlat
      use love, only : dklat
      use love, only : dllat
      use love, only : dtlat
      use love, only : dom0
      use love, only : domr
      use love, only : dgr
      use love, only : dhr
      use love, only : dkr
      use love, only : dlr
      use love, only : dtr
      external f2pysetupfunc
      call f2pysetupfunc(dglat,dhlat,dklat,dllat,dtlat,dom0,domr,dgr,dhr&
     &,dkr,dlr,dtr)
      end subroutine f2pyinitlove

      subroutine f2py_inout_getdims_etpdata(r,s,f2pysetdata,flag)
      use inout, only: d => etpdata

      integer flag
      external f2pysetdata
      logical ns
      integer r,i
      integer(8) s(*)
      ns = .FALSE.
      if (allocated(d)) then
         do i=1,r
            if ((size(d,i).ne.s(i)).and.(s(i).ge.0)) then
               ns = .TRUE.
            end if
         end do
         if (ns) then
            deallocate(d)
         end if
      end if
      if ((.not.allocated(d)).and.(s(1).ge.1)) then
       allocate(d(s(1),s(2)))
      end if
      if (allocated(d)) then
         do i=1,r
            s(i) = size(d,i)
         end do
      end if
      flag = 1
      call f2pysetdata(d,allocated(d))
      end subroutine f2py_inout_getdims_etpdata
      
      subroutine f2pyinitinout(f2pysetupfunc)
      use inout, only : argsin
      use inout, only : etpdata
      use inout, only : numwg
      use inout, only : fqmin
      use inout, only : fqmax
      use inout, only : ampf
      use inout, only : phasef
      use inout, only : exectime
      use inout, only : etd_start
      use inout, only : etd_end
      use inout, only : fileprd
      use inout, only : fileprn
      use inout, only : scrout
      use inout, only : etpol_start
      use inout, only : etpol_end
      use inout, only : isinit
      use inout, only : header
      use inout, only : etpunit
      use inout, only : cproj
      use inout, only : version
      use inout, only : vers
      use inout, only : fortvers
      external f2pysetupfunc
      external f2py_inout_getdims_etpdata
      call f2pysetupfunc(argsin,f2py_inout_getdims_etpdata,numwg,fqmin,f&
     &qmax,ampf,phasef,exectime,etd_start,etd_end,fileprd,fileprn,scrout&
     &,etpol_start,etpol_end,isinit,header,etpunit,cproj,version,vers,fo&
     &rtvers)
      end subroutine f2pyinitinout

