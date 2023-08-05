#Copyright 2009 Erik Tollerud
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License. 

"""

===================================================================
plotting -- astronomy-oriented matplotlib and mayavi plotting tools
===================================================================

The :mod:`plotting` module contains classes and funtions to aid in making plots
useful for astrophysics.

The 2D plots in this module all use the matplotlib_ package, while 3d plots are
a mix of matplotlib_ and mayavi_ .

.. _matplotlib: http://matplotlib.sourceforge.net/
.. _mayavi: http://code.enthought.com/projects/mayavi/

.. note::
    In this module and all other places astropysics uses matplotlib, 

.. todo:: examples

Module API
----------

"""

from __future__ import division,with_statement
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    from warnings import warn
    warn('Matplotlib not found - most 2D plotting will not work')

try:
    import enthought.mayavi
except ImportError:
    from warnings import warn
    warn('MayaVI 2 not found - most 3D plotting will not work')
    
from contextlib import contextmanager

#<----------------------------------matplotlib--------------------------------->
_mpl_show_default = False
@contextmanager
def mpl_context(show=None,clf=False,savefn=None):
    """
    Used for with statements containing matplotlib plots.  Usage::
    
        with _mpl_context() as plt:
            plt.plot(x,y,...)
            plt.scatter(xs,ys,...)
        
    :param bool show: 
        If True,:func:`pyplot.show` will be called when plotting is completed.
        This blocks execution until the user closes the plotting window.
    :param bool clf: If True, the figure will be cleared before plotting.
    :param savefn: 
        A string to save the figure to via the :func:`matplotlib.pyplot.savefig`
        function, or None to not save the figure.
    """
    if show is None:
        show = _mpl_show_default
    
    isinter = plt.isinteractive()
    try:
        if isinter:
            #TODO: figure out why this is necessary (probably an mpl/ipython problem)
            plt.gcf()
        plt.interactive(False)
        if clf:
            plt.clf()
            
        yield plt
        
    finally:
        plt.interactive(isinter)
        
    if savefn:
        plt.savefig(savefn)
    if show:
        plt.draw()
        plt.show()
    else:
        plt.draw_if_interactive()

def logerrplot(x,y,xerr=None,yerr=None,logaxes='y',boundscale=.5,**kwargs):
    """
    fixes log plots to be upper bounds in the event of zero-data or errorbars
    that go below zero
     
    logaxes can be 'x','y',or,'xy'
    """
    from numpy import where,array,zeros,ones,ndarray,float64
    from pylab import errorbar, semilogy,semilogx,loglog
    def fixaxis(data,err,lolims):
        data=array(data,dtype=float64)
        zeroinds=where(data <=0)[0]
        nonzeroinds=where(data > 0)[0]
        if err is None:
            #TODO:something smarter with the zeros?
            data[zeroinds]=boundscale*min(data[nonzeroinds])
            return data,None,lolims
        else:
            err=array(err)
            try:
                len(err)
            except:
                err=array([err])
            if len(err)==1: #single-symmetric errorbars
                newerr=ndarray((len(data),2))
                newerr.fill(err[0])
            elif len(err.shape) == 1: #vector symmetric errorbars
                newerr=ndarray((len(data),2))
                newerr[:,0]=err
                newerr[:,1]=err
            elif err.shape[0] == 2 : # vector asymmetric errorbars
                newerr=err.copy().T
            else:
                raise ValueError('Unrecognized form for error bars')
            
            
            lolims=array(lolims)
            try:
                len(lolims)
            except:
                lolims=array([lolims])
            if len(lolims)==1:
                lim=lolims[0]
                lolims=ndarray(len(data))
                lolims.fill(lim)
            assert len(lolims) == len(data), 'data and lower limits not same length'
            
            #first correct for data points that are zero by having them be upper limits
            data[zeroinds]=newerr[zeroinds,0]
            zeroerrs=zeros((len(zeroinds),2))
            zeroerrs[:,0]=data[zeroinds]*(boundscale)
            newerr[zeroinds]=zeroerrs
            lolims[zeroinds]=ones(len(zeroinds))
            
            
            #now replace errorbars that extend below zero with boundscale upper bounds
            negerrs=where(data-newerr[:,0] <= 0)[0]
            newerr[negerrs,0]=data[negerrs]*(boundscale)
            lolims[negerrs]=ones(len(negerrs))
            
            return data,newerr.T,lolims
            
            
    if 'lolims' in kwargs:
        lolims=kwargs.popd('lolims')
    else:
        lolims=False
    if 'xlolims' in kwargs:
        xlolims=kwargs.popd('xlolims')
    else:
        xlolims=False
        
    if logaxes == 'y':
        semilogy()
        y,yerr,lolims=fixaxis(y,yerr,lolims)
        ret=errorbar(x,y,xerr=xerr,yerr=yerr,lolims=lolims,xlolims=xlolims,**kwargs)
    elif logaxes == 'x':
        semilogx()
        x,xerr,xlolims=fixaxis(x,xerr,xlolims,**kwargs)
        ret=errorbar(x,y,xerr,yerr,lolims=lolims,xlolims=xlolims,**kwargs)
    elif logaxes == 'xy':
        loglog()
        x,xerr,xlolims=fixaxis(x,xerr,xlolims)
        y,yerr,lolims=fixaxis(y,yerr,lolims)
        ret=errorbar(x,y,yerr,xerr,lolims=lolims,xlolims=xlolims,**kwargs)
    else:
        raise ValueError('Unrecognized logaxes command')
    return ret
            
def add_mapped_axis(mapfunc,majorticks=5,minorticks=0,axis='x',label='',labelprops={},args=(),fmt='%3.1f',minfmt=None,invfunc=None):
    """
    mapfunc should accept a 1D numpy array as the first argument, and the args
    tuple will be passed as the rest of the arguments.  It should return an 
    array of the same length as the first argument.
    
    majorticks is the number of major ticks in the interval, while minorticks
    is the number of ticks between each majortick
    
    invfunc, if present, is used to make a linearly-spaced axis
    
    fmt and minfmt are either format specifiers for the value along the axis, or
    'sci%?' or 'pow%?' to use scientific notation
    
    if fmt is 'log#' or 'ln', a logarithmic axis will be assumed with the base given by #,
    and minfmt is ignored. (the function then just provides the edges)
    """
    from pylab import gca,xlim,ylim,twinx,twiny,axes,draw_if_interactive,xlabel,ylabel
    from numpy import array,arange,round,log,linspace,where,outer,all,ones,e
    from matplotlib.ticker import FixedLocator,FormatStrFormatter,FuncFormatter,NullFormatter,NullLocator
    from operator import isSequenceType
    
    oldax=gca()
    if axis == 'x':
        lims=xlim()
        newax = oldax.figure.add_axes(oldax.get_position(True), frameon=False)
        newax.set_xlim(*lims)
        axi= newax.xaxis
        axi.tick_top()
        axi.set_label_position('top')
        oldax.xaxis.tick_bottom()
        newax.yaxis.set_major_locator(NullLocator())
        newax.yaxis.set_minor_locator(NullLocator())
        newax.yaxis.set_major_formatter(NullFormatter())
        newax.yaxis.set_minor_formatter(NullFormatter())
        newax.set_xlabel(label,**labelprops)
    elif axis == 'y':
        lims=ylim()
        newax = oldax.figure.add_axes(oldax.get_position(True), frameon=False)
        newax.set_ylim(*lims)
        axi=newax.yaxis
        axi.tick_right()
        axi.set_label_position('right')
        oldax.yaxis.tick_left()
        newax.xaxis.set_major_locator(NullLocator())
        newax.xaxis.set_minor_locator(NullLocator())
        newax.xaxis.set_major_formatter(NullFormatter())
        newax.xaxis.set_minor_formatter(NullFormatter())
        newax.set_ylabel(label,**labelprops)
    else:
        raise ValueError('unrecognized axis type '+axis)
    
    if 'log' in fmt or 'ln' in fmt:
        base=fmt.replace('log','')
        if base == '':
            base = 10.0
        elif base =='ln':
            base = e
        else:
            base = float(base)
        
        if not minorticks:
            subs=None
        elif isSequenceType(minorticks):
            subs=minorticks
        else:
            subs=range(1,int(minorticks))
        
        loglims=log(array(mapfunc(lims)))/log(base)
        
        if majorticks >= abs(int(loglims[1])-int(loglims[0])):
            ticks=None
        elif 0 < majorticks < 1:
            dts=int(loglims[1])-int(loglims[0])
            ticks=10**round(arange(int(min(loglims)),int(max(loglims)),1/majorticks))
        elif majorticks:
            ticks=10**round(arange(min(loglims),max(loglims),abs(loglims[0]-loglims[1])/majorticks))
        else:
            ticks=None
        
        if axis == 'x':
            #newax.set_xlim(*mapfunc(lims))
            newax.set_xscale('log',basex=base,subsx=subs)
            axi.tick_top()
            if ticks is not None:
                axi.set_ticks(ticks)
            newax.set_xlim(*mapfunc(lims))
            axi.set_label_position('top')
        if axis == 'y':
            #newax.set_xlim(*mapfunc(lims))
            newax.set_yscale('log',basey=base,subsy=subs)
            axi.tick_right()
            if ticks is not None:
                axi.set_ticks(ticks)
            newax.set_ylim(*mapfunc(lims))
    else:
        
        
        x=linspace(lims[0],lims[1],majorticks+minorticks*(majorticks-1))
        xa=x[::(minorticks+1)]
        xi=x[all(xa!=outer(x,ones(len(xa))),axis=1)]
        
        axi.set_major_locator(FixedLocator(xa))
        axi.set_minor_locator(FixedLocator(xi))
        def make_mform(fmt,newaxis):
            if 'sci' in fmt:
                def sciform(x,pos):
                    t=(('%'+fmt.replace('sci','').replace('%','')+'e')  % mapfunc(x,*args)).split('e')
                    return '$%s \\times 10^{%i}$' % (t[0],int(t[1]))
                mform=FuncFormatter(sciform)
            elif 'pow' in fmt:
                def sciform(x,pos):
                    t=('%e'%mapfunc(x,*args)).split('e')
                    return '$10^{%i}$' % int(t[1])
                mform=FuncFormatter(sciform)
            else:
                mform=FuncFormatter(lambda x,pos:fmt%mapfunc(x,*args))
            return mform
        if fmt:
            mf=make_mform(fmt,axi)
            if mf is not None:
                axi.set_major_formatter(mf)
        if minfmt:
            mf=make_mform(minfmt,axi)
            if mf is not None:
                axi.set_minor_formatter(mf)
                
    axes(oldax)
    draw_if_interactive()
    

def scatter4d(x,y,c,s,xe=None,ye=None,logax=(False,False,False,False),scaling=(1,1,1,1),
              outlines=True,cb=True,errkwargs={},**kwargs):
    """
    cb can be used to specify the label of the colorbar
    
    returns collection,maskinds
    """
    with mpl_context() as plt:
        if c is None:
            c=np.ones(len(x))
        elif np.isscalar(c):
            c=c*np.ones(len(x))
        if s is None:
            s=np.ones(len(x))
        elif np.isscalar(s):
            s=s*np.ones(len(x))
        if len(x)!=len(y)!=len(c)!=len(s):
            raise ValueError('data arrays not same length')
        
        x=x*scaling[0]
        y=y*scaling[1]
        c=c*scaling[2]
        s=s*scaling[3]
        
        
        inds=set(np.arange(len(x)))
        if logax[0] and logax[1]:
            plt.loglog()
            inds.intersection_update(set(np.where(x>0)[0]))
            inds.intersection_update(set(np.where(y>0)[0]))
        elif logax[0]:
            plt.semilogx()
            inds.intersection_update(set(np.where(x>0)[0]))
        elif logax[1]:
            plt.semilogy()
            inds.intersection_update(set(np.where(y>0)[0]))
        if logax[2]:
            c=np.log10(c)
            inds.intersection_update(set(np.where(c>0)[0]))
        if logax[3]:
            s=np.log10(s)
            inds.intersection_update(set(np.where(s>0)[0]))
        inds=np.array(tuple(inds))
        
        if not outlines:
            kwargs['lw']=0
            
        
        if xe is not None or ye is not None:
            try:
                xei=xe[inds]
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                xei=xe
            try:
                yei=ye[inds]
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                yei=ye
            plt.errorbar(x[inds],y[inds],yei,xei,None,ecolor='k',**errkwargs)
        if 'zorder' not in kwargs:
            kwargs['zorder']=10
        scat=plt.scatter(x[inds],y[inds],s[inds],c[inds],**kwargs)
        
        if cb:
            cbo=plt.colorbar()
            if type(cb) == str:
                cbo.ax.set_ylabel(cb)
                
    return scat,inds

def square_subplot_dims(n):
    """
    returns (nrows,ncolumns) to optimize the space for n panels
    """
    ncols=np.ceil(np.sqrt(n))
    nrows=0
    while ncols*nrows < n:
        nrows += 1
    return (nrows,ncols)

def scatter_panel(p,plims,x,y,c=None,s=20,xe=None,ye=None,logax=(False,False,False,False),scaling=(1,1,1,1),
              pcfg=None,outlines=True,cb=True,xlab='',ylab='',plab='',xls=None,yls=None,errkwargs={},
              fitline=False,tsize=14,**kwargs):
    """
    pcfg is a 2-tuple of the form (rows,cols)
    
    kwargs go into pyplot.scatter
    
    fitline can be False/True or a dictionary that has line props and an
    optional 'annotate' key word for annotation (also 'asize' sets font size)
    """
    from matplotlib.colors import Normalize
    from operator import isMappingType
    from datanalysis import linear_lsq
    
    with mpl_context() as plt:
        if len(p)!=len(x):
            raise ValueError("p and data not same length")
        
        if not plab:
            plab='p'
            
        if np.isscalar(plims):
            ps=sorted(p)
            plims=[ps[int(i*len(ps)/plims)] for i in range(1,plims)]
        
        if pcfg is None:
            pcfg=square_subplot_dims(len(plims)+1)
        if (pcfg[0]*pcfg[1])<len(plims):
            raise ValueError('not enough panel space ')
        
        plims=list(plims)
        plims.insert(0,min(p))
        plims.append(max(p)+(max(p)-min(p))/1000) #TODO:more elegant way to get upper edge
        scats=[]
        try:
            colornorm=Normalize(vmin=min(c),vmax=max(c))
        except TypeError: #means a scalar or None was used for c, which is acceptable to pass along
            pass
        
        if not xls:
            xls=(np.min(x),np.max(x))
        if not yls:
            yls=(np.min(y),np.max(y))
        
        if fitline:
            if isMappingType(fitline):
                if logax[0] and logax[1]:
                    mask=x>0 & y>0
                    xlsq,ylsq=np.log10(x)[mask],np.log10(y)[mask]
                elif logax[0]:
                    mask=x>0
                    xlsq,ylsq=np.log10(x)[mask],y[mask]
                elif logax[1]:
                    mask=y>0
                    xlsq,ylsq=x[mask],np.log10(y)[mask]
                else:
                    xlsq,ylsq=x,y
                
                if 'fixslope' in fitline:
                    if fitline['fixslope'] is True:
                        fitline['fixslope']=linear_lsq(xlsq,ylsq)[0]
                    fixslope=fitline.pop('fixslope')
                else:
                    fixslope=False
                if 'fixint' in fitline:
                    if fitline['fixint'] is True:
                        fitline['fixint']=linear_lsq(xlsq,ylsq)[1]
                    fixint=fitline.pop('fixint')
                else:
                    fixint=False
                    
                if 'c' not in fitline and 'color' not in fitline:
                    fitline['c']='k'
                if 'ls' not in fitline and 'linestyle' not in fitline:
                    fitline['ls']='--'
                if 'annotate' in fitline:
                    ann=fitline.pop('annotate')
                else:
                    ann=False
                if 'asize' in fitline:
                    asize=fitline.pop('asize')
                else:
                    asize=10
                
            else:
                fixslope=fixint=None
                fitline={'c':'k','ls':'--'}
                ann=False
                
        for i in range(len(plims)-1):
            ind=np.where(np.logical_and(p>=plims[i],p<plims[i+1]))
            plt.subplot(pcfg[0],pcfg[1],i+1)
            try:
                ci=c[ind]
                kwargs['norm']=colornorm
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                ci=c
            try:
                si=s[ind]
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                si=s
            try:
                xei=xe[ind]
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                xei=xe
            try:
                yei=ye[ind]
            except TypeError: #means a scalar or None was used, which is acceptable to pass along
                yei=ye
                
            xi,yi=x[ind],y[ind]
            
            scats.append(scatter4d(xi,yi,ci,si,xei,yei,logax=logax,errkwargs=errkwargs,
                                   scaling=scaling,outlines=outlines,cb=False,**kwargs))
                
            if fitline:                
                if xls:
                    mask=np.logical_and(min(xls)<=xi,xi<=max(xls))
                else:
                    mask=np.ndarray(xi.shape)
                    mask.fill(True)
                if yls:
                    mask=np.logical_and(mask,np.logical_and(min(yls)<=yi,yi<=max(yls)))
                if logax[0] and logax[1]: #loglog
                    mask=np.logical_and(mask,np.logical_and(xi>0,yi>0))#make it safe for logs
                    
                    maski=np.where(mask)
                    xfi,yfi=xi[maski],yi[maski]
                    
                    m,b,dy,dm,db = linear_lsq(np.log10(xfi),np.log10(yfi),fixslope=fixslope,fixint=fixint)
                    xfp=np.logspace(np.log10(min(xfi)),np.log10(max(xfi)),200) 
                    yfp=10**(m*np.log10(xfp)+b)
                    stra='$\\log y=%0.3g\\log x+%0.3g $\n$\\sigma_x,\\sigma_y=\\pm %0.3g,\\pm %0.3g$\n$\\sigma = %0.3g$'%(m,b,dm,db,dy)
                elif logax[0]:
                    mask=np.logical_and(mask,xi>0)#make it safe for logs
                    
                    maski=np.where(mask)
                    xfi,yfi=xi[maski],yi[maski]
                    
                    m,b,dy,dm,db = linear_lsq(np.log10(xfi),yfi,fixslope=fixslope,fixint=fixint)
                    xfp=np.logspace(np.log10(min(xfi)),np.log10(max(xfi)),200) 
                    yfp=m*np.log10(xfp)+b
                    stra='$y=%0.3g\\log x+%0.3g $\n$\\sigma_x,\\sigma_y=\\pm %0.3g,\\pm %0.3g$\n$\\sigma = %0.3g$'%(m,b,dm,db,dy)
                elif logax[1]:
                    mask=np.logical_and(mask,yi>0)#make it safe for logs
                    
                    maski=np.where(mask)
                    xfi,yfi=xi[maski],yi[maski]
                    
                    m,b,dy,dm,db = linear_lsq(xfi,np.log10(yfi),fixslope=fixslope,fixint=fixint)
                    xfp=np.linspace(min(xfi),max(xfi),200)
                    yfp=10**(m*xfp+b)
                    stra='$\\log y=%0.3gx+%0.3g $\n$\\sigma_x,\\sigma_y=\\pm %0.3g,\\pm %0.3g$\n$\\sigma = %0.3g$'%(m,b,dm,db,dy)
                else: #simple linear
                    maski=np.where(mask)
                    xfi,yfi=xi[maski],yi[maski]
                    
                    m,b,dy,dm,db = linear_lsq(xfi,yfi,fixslope=fixslope,fixint=fixint)
                    xfp=np.linspace(min(xfi),max(xfi),200)
                    yfp=m*xfp+b
                    stra='$y=%0.3gx+%0.3g $\n$\\sigma_x,\\sigma_y=\\pm %0.3g,\\pm %0.3g$\n$\\sigma = %0.3g$'%(m,b,dm,db,dy)
                    
                plt.plot(xfp,yfp,**fitline)
                if ann:
                    stra,strl=stra.split('\n'),[]
                    if ann is True:
                        ann=tuple([True for i in stra])
                    for i,t in enumerate(ann):
                        if t:
                            strl.append(stra[i])
                    plt.annotate('\n'.join(strl),(xfp[len(xfp)/2],yfp[len(xfp)/2]),size=asize)
                
            plt.title('%0.3g <= %s < %0.3g'%(plims[i],plab,plims[i+1]),fontsize=tsize)
            
            if xlab:
                plt.xlabel(xlab,fontsize=tsize)
            if ylab:
                plt.ylabel(ylab,fontsize=tsize)
            plt.xlim(*xls)
            plt.ylim(*yls)
                
        if cb and np.any(c):
            try:
                axo=plt.subplot('%i%i%i'%(pcfg[0],pcfg[0],len(plims)),aspect=20)
                cbo=plt.colorbar(scats[-1],cax=axo)
            except ValueError:
                cbo=plt.colorbar(scats[-1])
            if type(cb) == str:
                cbo.ax.set_ylabel(cb)
            
    return scats

def dual_value_plot(x,y1,y2,fmt='-o',yerrs=None,xerrs=None,**kwargs):
    """
    plots dual-valued functions
    kwargs go to errorbar function
    """
    raise NotImplementedError
    from operator import isSequenceType
    if yerrs is None:
        yerrs=[None for xi in x]
    if xerrs is None:
        xerrs=[None for xi in x]
    if 'c' in kwargs and isSequenceType(kwargs['c']):
        raise NotImplementedError('color sequence not working yet')
    if len(x) != len(y1) != len(y2) != len(yerrs) != len(xerrs):
        raise ValueError('All arrays not same length')
        
    with mpl_context() as plt:
        for xi,y1i,y2i,yei,xei in zip(x,y1,y2,yerrs,xerrs):
            plt.errorbar((xi,xi),(y1i,y2i),yei,xei,'o-',**kwargs)
        
def scatter_select(*args,**kwargs):
    """
    quick scatter plot to lasso objects and return an object that will be
    updated with the selections
    
    args and kwargs go into matplotlib scatter except for 'close' which 
    is used to close the current figure on function call(default True)
    
    returns a dictionary that will be populated with 'i','xis', and'yi' , and
    possibly 'ci' or 'si' if c or s are in the scatter plot
    """
    import time
    from matplotlib.widgets import Lasso
    
    if kwargs.pop('close',True):
        plt.close()
    sca=plt.scatter(*args,**kwargs)
    ax=plt.gca()
    canvas=ax.figure.canvas
    
    x,y=args[0],args[1]
    
    if len(args)>2:
        s = args[2]
    elif 's' in kwargs:
        s = kwargs['s']
    else:
        s = None
    
    if len(args)>3:
        c = args[3]
    elif 'c' in kwargs:
        c = kwargs['c']
    else:
        c = None
    
    d={}
    
    
    def callback(verts):
        from matplotlib.nxutils import points_inside_poly
        
        xy = np.array((x,y)).T
        inds = np.nonzero(points_inside_poly(xy,verts))[0]
        
        canvas.widgetlock.release(d['las'])
        
        del d['las']
        
        
        d['i']=inds.astype(int)
        d['xi']=x[inds]
        d['yi']=y[inds]
        if s is not None:
            d['si']=s[inds]
        if c is not None:
            d['ci']=c[inds]
    
    def onpress(event):
        plt.draw() #erases lasso
        if canvas.widgetlock.locked():
            raise Exception('widgetlock active')
        d['las'] = Lasso(event.inaxes, (event.xdata,event.ydata),callback)
        canvas.widgetlock(d['las'])
    
    cid=canvas.mpl_connect('button_press_event', onpress)
    
    return d
    

class ScatterLasso(object):
    def __init__(self,ax=None,xys=None):
        if ax is None:
            ax=plt.gca()
        self.ax=ax
        self.canvas=ax.figure.canvas
        self.cid=None
        self.xys=None
        self.inds=None
        self.keydict,self.keyxattr,self.keyyattr=None,None,None
        
        #TODO: extract xy data from axes
        self.xyin = xys
        
    def onpress(self,event):
        from matplotlib.widgets import Lasso
        plt.draw() #for some reason this works while self.canvas.draw doesnt
        
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.las = Lasso(event.inaxes, (event.xdata,event.ydata),self.callback)
        self.canvas.widgetlock(self.las)
    
    def callback(self,verts):
        from matplotlib.nxutils import points_inside_poly
        
        
        inds=[]
        for xy in self.xys:
            inds.append(np.nonzero(points_inside_poly(xy,verts))[0])
        
        self.canvas.widgetlock.release(self.las)
        self.inds = inds
        
        del self.las
    
    def activateLasso(self):
        self.xys=[]
        for art in self.ax.get_children():
            if hasattr(art,'_offsets'):
                self.xys.append(np.array(art._offsets))
                
        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
        self.cid=self.canvas.mpl_connect('button_press_event', self.onpress)
        
    def deactivateLasso(self):
        self.canvas.mpl_disconnect(self.cid)
        self.cid=None
        plt.draw() #for some reason this works to clear the lassos while self.canvas.draw doesnt
    
    def getLastXYs(self):
        xya=[]
        for i,ind in enumerate(self.inds):
            xya.extend(self.xys[i][ind])
        return np.array(xya)
    
    def matchLastXYs(self,xyin,map=None):
        """
        takes the last set of xys and matches them to an NX2 array of x,y values,
        returning indecies into the 1st dimension
        """
        if xyin == None:
            xyin = self.xyin
        else:
            self.xyin = xyin
        if xyin is None:
            raise ValueError('no xy values provided')
        
        lxys=self.getLastXYs()
        #TODO:optimize if slow w/numpy operations
        matchis=[]
        for lxy in lxys:
            for i,xyj in enumerate(xyin):
                if np.all(lxy==xyj):
                    matchis.append(i)
            
        if map:
            return [map[k] for k in matchis]
        else:
            return np.array(matchis)
    
    def getLastInds(self):
        return self.inds
    
    def getLastKeys(self,d=None,xattr='x',yattr='y'):
        if d is None:
            d=self.keydict
        else:
            self.keydict=d
        if xattr is None:
            xattr=self.keyxattr
        else:
            self.keyxattr=xattr
        if yattr is None:
            yattr=self.keyyattr
        else:
            self.keyyattr=yattr
        if d is None or xattr is None or yattr is None:
            raise ValueError('must fully specify key/dict details')
        
        xys = np.array([(getattr(v,xattr),getattr(v,yattr)) for v in d.values()])
        return self.matchLastXYs(xys,map=d.keys())
            

def subplots_adjust_points(left=None,bottom=None,right=None,top=None, 
                           wspace=None,hspace=None,fig=None):
    """
    Performs the same operation as :func:`matplotlib.pyplot.subplots_adjust` but
    uses point size uinits instead of fractions of the total figure size.
    """
    if fig is None:
        fig=plt.gcf()
    w,h=fig.get_figwidth(),fig.get_figheight()
    dpi=fig.get_dpi()
    l=left/dpi/w if left is not None else None
    b=bottom/dpi/h if bottom is not None else None
    r=1-right/dpi/w if right is not None else None
    t=1-top/dpi/h if top is not None else None
    ws=wspace/dpi/w if wspace is not None else None
    hs=hspace/dpi/h if hspace is not None else None
    plt.subplots_adjust(l,b,r,t,ws,hs)
    
        
        
def scatter_density(x,y,bins=20,threshold=None,ncontours=None,contf=False,cb=False,
                    clf=True,bingrid=False,xlog=False,ylog=False,points=False,
                    lims=None,skwargs={},ckwargs={}):
    """
    plots x vs. y, scatter plotting where the number is below the threshold, 
    contouring if above
    
    bins is the number of bins or [xbins,ybins]
    
    ncontours defaults to bins/3
    
    threshold defaults to whatever fills half the histogram
    
    lims can be None or (xmin,xmax,ymin,ymax)
    
    skwargs goes into scatter(), ckwargs goes into contour() or contourf() 
    
    .. warning:: 
        This function will likely be adapted to use
        :func:`matplotlib.pyplot.hexbin` in the near future instead of contour
        or contourf, so don't expect it to stay consistent until that happens
    """
    from matplotlib.colors import Normalize
    
    if ncontours is None:
        ncontours = int(np.ceil(np.array(bins,ndmin=1).mean()/3.0))+1
        
    if lims is not None:
        xmin,xmax,ymin,ymax=lims
        m= (xmin <= x) & (x <= xmax) & (ymin <= y) & (y <= ymax)
        x,y=x[m],y[m]
    
    n,xe,ye=np.histogram2d(x,y,bins=bins)
    n = n.astype(int)

    if threshold is None:
        hn = n.flatten()[np.argsort(n,axis=None)]
        threshold = int(np.ceil(hn[hn.size/6]))
    
    cbins=n >= threshold
    sbins=n < threshold
    assert np.all(cbins | sbins),'not all bins populated!'
    
    #n[sbins]=0
    
    cx=np.convolve(xe,(0.5,0.5),'valid')
    cy=np.convolve(ye,(0.5,0.5),'valid')
    
    ms = np.zeros_like(x).astype(bool)
    xis,yis=np.where(sbins)
    for i in range(len(xis)):
        xl,xu = xe[xis[i]],xe[xis[i]+1]
        yl,yu = ye[yis[i]],ye[yis[i]+1]
        mi = (xl < x) & (x < xu) & (yl < y) & (y < yu)
        ms = ms | mi
        
    reses=[]
    with mpl_context(clf=clf) as plt:
        #norm=Normalize(vmin=threshold,vmax=np.max(n))
        #ckwargs['norm']=norm
        contours=np.linspace(threshold,np.max(n),ncontours)
        if contf:
            cp = plt.contourf(cx,cy,n.T,contours,**ckwargs)
        else:
            cp = plt.contour(cx,cy,n.T,contours,**ckwargs)
        reses.append(cp)
            
        
        if cb:
            if int(cb)>1:
                tks = np.linspace(threshold,np.max(n),int(cb))
            else:
                tks = None
            if type(cb) is str:
                cb = plt.colorbar(orientation=cb,ticks=tks)
            else:
                cb = plt.colorbar(orientation='horizontal',ticks=tks)
            reses.append(cb)
            
        if sum(ms) > 0:
            if points:
                sp=plt.plot(x,y,'.',ms=int(points),c='k')
            else:
                sp = plt.scatter(x[ms],y[ms],**skwargs)    
            reses.append(sp)
            
        if bingrid:
            reses.append(plt.vlines(xe,ye[0],ye[-1],color='k',linestyles='-',lw=1))
            reses.append(plt.hlines(ye,xe[0],xe[-1],color='k',linestyles='-',lw=1))
        if xlog and ylog:
            plt.loglog()
        elif xlog:
            plt.semilogx()
        elif ylog:
            plt.semilogy()
        plt.xlim(xe[0],xe[-1])    
        plt.ylim(ye[0],ye[-1])  
        
        
    return tuple(reses)


def cumulative_plot(data,Nlt=True,frac=False,xlabel='x',edges=(None,None),
                    logx=False,logy=False,doplot=True,perr=False,**kwargs):
    """
    Plots a 1d sequence of data points as a cumulative count less than (or 
    greater than) a given value - i.e. the integrated histogram. 
    
    :param data: input data for plot
    :type data: array-like
    :param bool Nlt: If True, produces N(<x) plot, otherwise N(>x).
    :param frac: 
        If False, the raw N will be plotted. If True, the cumulative fraction
        will be plotted(e.g. it will always terminate at 1), or if a scalar, the
        fraction will be multiplied by that value.
    :type frac: bool or scalar
    :param xlabel: Label for the data value.
    :type xlabel: string
    :param edges: 
        Specifies the lower and upper limits for the plot. If not provided, the
        lowest and highest of `data` will be used.  If data is below or above 
        these edges, it will be ignored.
    :type edges: tuple of scalars or Nones
    :param bool logx: Logarithmic x-axis?
    :param bool logy: Logarithmic y-axis?
    :param bool doplot: 
        If True, the plotting function is called. Otherwise no plot is made, but
        the x and y values are still generated and returned (allowing for more
        customized plots).
    :param perr: 
        If True, shaded error regions are added assuming poisson errors.  Can be
        a dict giving kwargs for :func:`matplotlib.pyplot.fill_between`.
    
    kwargs are passed into :func:`matplotlib.pyplot.plot`
    
    :returns: (val,N) i.e. the x and y values of the resulting plot. 
    
    """
    from matplotlib import pyplot as plt
    from operator import isMappingType
    
    #both ls and linestyle can be used to set the style, so we don't 
    #differentiate unless both are missing
    if 'ls' in kwargs:
        kwargs['ls'] = 'steps' + kwargs['ls']
    if 'linestyle' in kwargs:
        kwargs['linestyle'] = 'steps' + kwargs['linestyle']
    if 'ls' not in kwargs and 'linestyle' not in kwargs:
        kwargs['ls'] = 'steps'
        
    
    x = np.array(data).ravel()
    x.sort()
    y = np.arange(x.size)
    
    if not Nlt:
        x = x[::-1]
        
    if edges[0] is not None:
        lmask = x>edges[0]
        x = x[lmask]
        y = y[lmask]
        x = np.insert(x,0,edges[0] if Nlt else edges[1])
        y = np.insert(y,0,0)# if Nlt else y[-1])
    if edges[1] is not None:
        umask = x<edges[1]
        x = x[umask]
        y = y[umask]
        x = np.append(x,edges[1] if Nlt else edges[0])
        y = np.append(y,y[-1]+1)# if Nlt else 0)
        
    if frac:
        frac = float(frac) #True->1.0
        finalN = y[-1]
        y = y*frac/finalN
            
    if logx and logy:
        pltfunc = plt.loglog
    elif logx:
        pltfunc = plt.semilogx
    elif logy:
        pltfunc = plt.semilogy
    else:
        pltfunc = plt.plot
    
    if doplot:
        with mpl_context() as plt:
            
            pltres = pltfunc(x,y,**kwargs)[0]
            plt.xlabel(xlabel)
            ltgt = '<' if Nlt else '>'
            if '$' in xlabel:
                plt.ylabel('$N(%s%s)$'%(ltgt,xlabel.replace('$','')))
            else:
                plt.ylabel('N(%s%s)'%(ltgt,xlabel))
                
            #plot error region first if needed
            if perr:
                from matplotlib import colors
                
                if perr is True:
                    perr = {}                    
                if frac:
                    N1 = y*finalN/frac
                    N2 = finalN
                    ferr = (1./N1 + 1./N2)**0.5
                else:
                    ferr = y**-0.5
                    
                perr.setdefault('zorder',pltres.get_zorder()-.1)
                rgba = list(colors.colorConverter.to_rgba(pltres.get_color()))
                rgba[-1] *= .5
                perr.setdefault('color',tuple(rgba))
                
                plt.fill_between(x,y*(1-ferr),y*(1+ferr),**perr)
                
            
    return x,y
        
        
def split_histograms(vals,edgevals,edges,bins=None,clf=True,colors=None,
                     styles=None,edgename='',**kwargs):
    """
    Generates histograms in the first parameter that are split over ranges based
    on a second parameter.
    
    :param vals: values for generating the histograms
    :type vals: array-like
    :param edgevals: values to use for splitting the histograms
    :type edgevals: array-like
    :param edges: 
        A sequence of values giving the boundaries in the `edgeval` space for
        each of the histograms (lower bound is inclusive).  Must be 
        monotonically increasing.
    :type edges: sequence with len>1
    :param bins: 
        Bins for the `vals` following the form of
        :func:`matplotlib.pyplot.hist`.  If None or an integer, the bins
        will be inferred from the full data set.
    :param clf: if True, the current figure will be cleared before plotting
    :type clf: bool
    :param colors: line colors for each histogram or None for default
    :type styles: sequence of strings or None
    :param styles: line styles for each of the histograms or None for default 
    :type styles: sequnce of strings or None
    :param edgename: Name of the variable for the edges (used in legend)
    :type edgename: string

    kwargs are passed into the calls to :func:`matplotlib.pyplot.hist`
    """
    if len(edges)<2:
        raise ValueError('edges must be length>1')
    if colors is not None and len(edges)-1!=len(colors):
        raise ValueError('colors must by length of edges minus one')
    if styles is not None and len(edges)-1!=len(styles):
        raise ValueError('styles must by length of edges minus one')
    
    vals = np.array(vals,copy=False)
    edgevals = np.array(edgevals,copy=False)
    if vals.shape != edgevals.shape:
        raise ValueError('vals and edgevals do not have matching shapes')
    
    valslist = []
    hstrs = []
    for i in range(len(edges)-1):
        l = edges[i]
        u = edges[i+1]
        if not l<u:
            raise ValueError('edges not monotonically increasing')
        valslist.append(vals[(l<=edgevals)&(edgevals<u)])
        if edgename == '':
            hstrs.append('[%.3f,%.3f)'%(l,u))
        else:
            hstrs.append(r'$%.3f \leq %s<%.3f$'%(l,edgename,u))
    
    if bins is None:
        bins = np.histogram(vals)[1]
    elif isinstance(bins,int):
        bins = np.histogram(vals,bins=bins)[1]
    
    kwargs.setdefault('histtype','step')
    lsmap = {'-':'solid','--':'dashed','-.':'dashdot',':':'dotted',
             'solid':'solid','dashed':'dashed','dashdot':'dashdot','dotted':'dotted'}
    
    with mpl_context(clf=clf) as plt:
            
        maxh = -1
        for i,v in enumerate(valslist):
            if colors is not None:
                kwargs['color'] = colors[i]
            if styles is not None:
                kwargs['ls'] = lsmap[styles[i]]
            kwargs['label'] = hstrs[i]
            kwargs['bins'] = bins
            count = plt.hist(v,**kwargs)[0]
            maxh = max(maxh,np.max(count))
            
        plt.ylim(0,maxh)
        
def plot_histogram(nbin,binedges,**kwargs):
    """
    Uses the 'steps' line style to make histograms from bin data like that
    output from :func:`numpy.histogram`. While similar in functionality to
    :func:`matplotlib.pyplot.hist`, it allows the histogram data to be modfied
    instead of being computed in the function and accepts keywords like
    :func:`matplotlib.pyplot.plot`.
    
    :param nbin: Number of histogram items in each bin.
    :param binedges: Edge values for bins, should be of size len(nbin)+1.
    
    Additional keywords are passed into :func:`matplotlib.pyplot.plot`.
    
    """
    clf = kwargs.pop('clf',False)
    with mpl_context(clf=clf) as plt:
        kwargs.setdefault('drawstyle','steps')
        plt.plot(np.concatenate((binedges,[binedges[-1]])),
                 np.concatenate(([0],nbin,[0])),**kwargs)
        
def ax3d_animate(azels,nframes,fn,fig=None,initazel=None,relative=True,
                 predelete=False,verbose=False,savekwargs={}):
    """
    Animates a figure made in matplotlib using the mplot3d 3D plotting tools.
    
    :param azels: 
        Specifies the azimuth ane elevation to use for the key frames - each
        segment will have `nframes` and linearly interpolate azimuth and
        elevation between the `azels` values. If `relative` is True, the values
        are offsets (in degrees) from the previous key frame. Otherwise, they
        are absolute values (in degrees). If equal in length to `nframes`, the
        initial frame is chosen based on the azim and elev when the function is
        called. If len(`nframes`) == len(`nazels`)-1, the initial frame is taken
        to be the first in `azels` (absolute, regardless of the `relative`
        keyword value).
    :type azels: sequence of (azim,elev) tuples
    :param nframes: Number of frames per segment (see `azels` for lengths).  
    :type nframes: sequence of ints
    :param fn: 
        The filename to use to save the animation frames. If the substring
        '{fnum}' appears anywhere in this name, the frame number will be added
        there. Otherwise, the frame number is added before the extension. If
        None, no files are actually saved - the animation just plays in the
        window.
    :type fn: string or None
    :param fig: The figure to use for the animation.
    :type fig: :class:`matplotlib.figure.Figure` object, int, or None
    :param relative: 
        If True, ` azels`are relative to previous frame. Otherwise, they are
        absolute.
    :type relative: bool
    :param predelete: 
        If True, all files matching the pattern will be deleted before saving of
        a new set of frames occurs.
    :type predelete: bool
    :param verbose: If True, info is printed for each frame.
    :type verbose: bool
    :param savekwargs: keyword arguments for :func:`matplotlib.pyplot.savefig`
    :type savekwargs: dict
    
    :except ValueError: If `azels` and `nframes` don't have valid lengths
    :except TypeError: If the current figure doesn't have one Axes3D 
    
    """
    
    import os,sys,glob
    
    if fn is not None and '{fnum}' not in fn:
        fn = '_{fnum}'.join(os.path.splitext(fn))
        
    if fn is not None and predelete:
        for dfn in glob.glob(fn.replace('{fnum}','*')):
            if os.path.isfile(dfn):
                if verbose:
                    print 'deleting',dfn
                os.remove(dfn)
        
    if fig is None:
        fig = plt.gcf()
    elif isinstance(fig,int):
        fig = plt.figure(fig)
        
    if len(fig.axes) !=1:
        raise TypeError('Figure does not have just 1 axis')
    ax = fig.axes[0] 
    if not hasattr(ax,'azim') or not hasattr(ax,'elev'):
        raise TypeError('axis is not 3D')
    
    if len(azels) == len(nframes):
        azel0 = None
    elif len(azels)==len(nframes)+1:
        azel0 = azels[0]
        azels = azels[1:]
    else:
        raise ValueError('Invalid lengths for azels and nframes')
    
    if azel0 is not None:
        ax.azim = azel0[0]
        ax.elev = azel0[1]
    
    frames = []
    if relative:
        for (az,el),nf in zip(azels,nframes):
            dazim = az/nf
            delev = el/nf
            frames.extend([(dazim,delev)]*nf)
    else:
        azlast = ax.azim
        ellast = ax.elev
        for (az,el),nf in zip(azels,nframes):
            dazim = (az-azlast)/nf
            delev = (el-ellast)/nf
            frames.extend([(dazim,delev)]*nf)
            azlast = az
            ellast = el 
    
    #format string for frame count
    frmstr = '%0'+str(len(str(len(frames))))+'i'
    
    fig.canvas.draw()
    if fn is not None:
        saveargs = [fn.replace('{fnum}',frmstr%0)]
        fig.savefig(*saveargs,**savekwargs)
    for i,(az,el) in enumerate(frames):
        if verbose:
            print 'Frame',i+1,'of',len(frames),':'
            print 'From',(ax.azim,ax.elev),'adding',(az,el)
            if fn is not None:
                print 'saving',fn.replace('{fnum}',frmstr%i)
        ax.azim += az
        ax.elev += el
        fig.canvas.draw()
        if fn is not None:
            saveargs = [fn.replace('{fnum}',frmstr%i)]
            fig.savefig(*saveargs,**savekwargs)
    


#<------------------------------------Maya VI---------------------------------->

def mlab_anaglyph(dostereo=True,anasat=0,anamask=[4,3]):
    """
    Switch :mod:`enthought.mayavi.mlab` to use "checkerboard" style stereo
    
    :param bool dostereo: 
        Turns on stereo if True, off if False, or if None, toggles stereo mode.
    :param float anasat: saturation for anaglyph mode
    :param 2-sequence anamask: color mask for anaglyph mode
    
    :returns: the VTK render window object
    """
    from enthought.mayavi import mlab as M
    
    w = M.gcf().scene.renderer.render_window
    w.stereo_type = 'anaglyph'
    w.anaglyph_color_mask = anamask
    w.anaglyph_color_saturation = anasat
    if dostereo is None:
        dostereo = not w.stereo_render 
    else:
        w.stereo_render = bool(dostereo)
    return w

def mlab_checkerboard(dostereo=True):
    """
    Switch :mod:`enthought.mayavi.mlab` to use "checkerboard" style stereo
    
    :param dostereo: 
        Turns on stereo if True, off if False, or if None, toggles stereo mode.
    
    
    :returns: the VTK render window object
    """
    from enthought.mayavi import mlab as M
    
    w = M.gcf().scene.render_window
    w.stereo_type = 'checkerboard'
    if dostereo is None:
        dostereo = not w.stereo_render 
    else:
        w.stereo_render = bool(dostereo)
    return w
    

def mlab_camera(fp=None,pos=None,angle=None,dorender=True):
    """
    Adjust :mod:`enthought.mayavi.mlab` camera based on a position and focal 
    point rather than angles as used by :func:`enthought.mayavi.mlab.` .
    
    :param fp: An (x,y,z) sequence for the focal point or None to leave alone.
    :param pos: 
        An (x,y,z) sequence for the camera position  or None to leave alone.
    :param angle: The field-of-view angle in degrees or None to leave alone.
    :param bool dorender: 
        If True, the scene will be re-rendered at the end of this function.
        
    :returns: The VTK Camera object
    """
    from enthought.mayavi import mlab as M
    s = M.gcf().scene
    c = s._renderer.active_camera
    if fp is not None:
        try:
            if len(fp) != 3:
                raise ValueError('focal point must be a length-3 sequence or scalar')
            c.focal_point = fp
        except: #scalar
            oldfp=c.focal_point
            normedfp=oldfp*(oldfp*oldfp).sum()**-0.5
            c.focal_point=fp*normedfp
    if pos is not None:
        if len(pos) != 3:
            raise ValueError('Position must be a length-3 sequence')
        c.position = pos
    if angle is not None:
        c.view_angle=angle
        
    s.renderer.reset_camera_clipping_range()
    if dorender:
        s.render()
    
    return c

def mlab_animate_rotzoom(fnbase,azs=None,els=None,rolls=None,dists=None,
                              relative=True,fps=None,ui=False,figsize=None):
    """
    This generates an animation using the :func:`mlab.animate` mechanism that
    rotates the scene and possibly zooms in and out with a fixed focal point.
     
    :param azs: 
        A sequence of azimuthal angles (in degrees), a single angle to apply on
        every frame, or None to not change the angle.
    :param els: 
        A sequence of elevation angles (in degrees), a single angle to apply on
        every frame, or None to not change the angle.
    :param rolls: 
        A sequence of roll angles (in degrees), a single angle to apply on
        every frame, or None to not change the angle.
    :param dists: 
        A sequence of distances, a single angle to apply on every frame, or None
        to not change the angle.
    :param bool relative:
        If True, the `azs`,`els`, and `rolls` angles are relative to the current
        orientation, and `dists` is a multiple of the current distance.
        Otherwise, the quantities are absolute angles and distances.
    :param fnbase: 
        The filename for the files (_### will be added between the extension and
        filename) or None to just show the animation and not save. The file type
        will be inferred from the extension, but if no extension is given, .png
        will be used.
    :param fps: 
        Sets the approximate number of frames per second for the animation as it
        plays - set to None for no delay between frames.
    :param bool ui: 
        If True, a GUI will be available while the animation is running to pause
        or stop the animation.  If False, the GUI will not be shown.
    :param figsize: 
        The resolution at which to save the figure as a (xpix,ypix) tuple or
        None to just use the window size.
    
    
    :returns: 
        (anim,fnlist) `anim` is an animator of the sort that
        :func:`mlab.animate` returns -- call this animator to start the
        animation. `fnlist` is a list of filenames that have been saved - it
        will initially be empty, but once the animation is run, it will be
        populated.
   
    """
    from enthought.mayavi import mlab
    import os
        
    ns = []
    for v in (azs,els,rolls,dists):
        try:
            ns.append(len(v))
        except:
            ns.append(None)
    n = max(ns)
    if n is None:
        raise ValueError('no make_movie inputs are arrays!')
    if any([e!=n for e in ns if e is not None]):
        raise ValueError("arrays don't match!")
    
    if ns[0] is None:
        azs = [azs]*n
    if ns[1] is None:
        els = [els]*n
    if ns[2] is None:
        rolls = [rolls]*n
    if ns[3] is None:
        dists = [dists]*n
        
    if fnbase is not None:    
        fnn,fne = os.path.splitext(fnbase)
        if fne == '':
            fne = '.png'
        fnpat = '{0}_{2:0'+str(int(np.ceil(np.log10(n))))+'}{1}'
    
    if fps is None:
        delay=10
    else:
        delay = int(round(1000/fps)) #30 FPS goal
    
    fnlist = []
    
    @mlab.show
    @mlab.animate(delay=delay,ui=ui)
    def anim_gen():
        oldview = initview = mlab.view()
        oldroll = initroll = mlab.roll()
        print 'init',initview,initroll
        
        for i,(az,el,roll,dist) in enumerate(zip(azs,els,rolls,dists)):
            if fnbase is not None:
                savefn = fnpat.format(fnn,fne,i)
                print 'Saving',savefn,'of',len(azs)
                mlab.savefig(savefn,size=figsize)
                fnlist.append(savefn)
            if relative:
                s = mlab.gcf().scene
                if az is not None:
                    s.camera.azimuth(az)
                if el is not None:
                    s.camera.elevation(el)
                if roll is not None:
                    s.camera.roll(roll)
                if dist is not None:
                    s.camera.dolly(1/dist)
                s.renderer.reset_camera_clipping_range()
                s.render()
            else:
                if az is None:
                    az = oldview[0]
                if el is None:
                    el = oldview[1]
                if dist is None:
                    dist = oldview[2]
                mlab.view(az,el,dist,oldview[3],reset_roll=False)
                mlab.roll(roll)
                
                oldview = mlab.view()
                oldroll = mlab.roll()
            yield
                
        mlab.view(*initview)
        mlab.roll(initroll)
    return anim_gen,fnlist

def mvi_texture(s,texture,genmode='plane'):
    """
    Generates a texture and applies it to a mayavi surface.
    
    :param s: 
        A :class:`enthought.mayavi.modules.surface.Surface` object or None to
        only load the texture.
    :param texture: 
        A :class:`enthought.mayavi.sources.api.ImageReader` object or a file 
        name for an image to be used as the texture.
    :param genmode: 
        The tcoord_generator_mode to use. Should be 'none' or 'cylinder' or
        'sphere' or 'plane'. Ignored if `s` is None. See
        :class:`enthought.mayavi.modules.surface.Surface` docs for more details.
    
    :returns: The :class:`enthought.mayavi.modules.surface.Surface` object 
    
    """
    from enthought.mayavi.sources.api import ImageReader
    from enthought.persistence.file_path import FilePath
    
    fp = FilePath(fn)
    ir = ImageReader(file_path=fp)
    
    if s is not None:
        s.actor.tcoord_generator_mode = genmode
        s.actor.texture_source_object = texture
        s.actor.mapper.scalar_visibility = False
        s.actor.enable_texture = True
    
    return ir

#<-----------------------------------Generic/utility--------------------------->
def make_movie(frfn,moviefn,framerate=30,bitrate='200k',inops=None,outops=None,
                            run=True):
    """
    Given a base file name where movie frame files have been saved, generates a
    movie using `ffmpeg <http://www.ffmpeg.org/>`_. This is intended to be used
    with the :func:`*_animate` functions in this module, but can be used for any
    set of filenames that follow the correct pattern and define movie frames.
    
    `ffmpeg <http://www.ffmpeg.org/>`_ must be installed for this function to
    work.
    
    :param frfn: 
        The filename to use to locate the animation frames. If the substring
        '{fnum}' appears anywhere in this name, the frame number will be added
        there. Otherwise, the frame number is added before the extension. This
        is the same form as the same as the input to :func:`ax3d_animate` or
        :func:`mlab_animate_rotzoom`.
    :type frfn: string
    :param moviefn: Filename to use for the output movie
    :type moviefn: string
    :param inops: dictionary mapping ffmpeg options to their values for input
    :type inops: dict or None
    :param outops: dictionary mapping ffmpeg options to their values for output
    :type outops: dict or None
    :param bool run: 
        If True, ffmpeg is actually called. Otherwise, no movie is made, but
        the returned string can be executed at the command line.
        
    :returns: A string with the command line call to ffmpeg
    
    
    :except ValueError: 
        If the ffmpeg call does not complete sucessfully or there are no
        matching files.
        
    """
    
    import os,glob
    
    if '{fnum}' not in frfn:
        frfn = '_{fnum}'.join(os.path.splitext(frfn))
        
    pre,post = frfn.split('{fnum}')
    fns = glob.glob(pre+'*'+post)
    
    if inops is None:
        inops = []
    else:
        tempops = []
        for name,val in inops.iteritems():
            temp.append('-'+name)
            temp.append(val)
        inops = tempops
        
    if outops is None:
        outops = []
    else:
        tempops = []
        for name,val in outops.iteritems():
            temp.append('-'+name)
            temp.append(val)
        outops = tempops
    
    inops = ' '+' '.join(inops)
    outops= ' '+' '.join(outops)
    
    if len(fns)<1:
        raise ValueError('No files matching pattern %s were found'%(pre+'*'+post))
    ffmpeginstr = pre+'%0'+str(len(fns[0])-len(pre)-len(post))+'d'+post
    
    callt = (inops,framerate,bitrate,ffmpeginstr,outops,moviefn)
    ffmpegcall = 'ffmpeg%s -r %s -b %s -i %s%s %s'%callt
    
    retcode = os.system(ffmpegcall)
    if retcode != 0:
        raise ValueError('ffmpeg did not complete correctly - return code %i'%retcode)
    return ffmpegcall

#clean up namespace
del contextmanager
