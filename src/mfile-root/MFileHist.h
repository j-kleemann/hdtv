/*
 * HDTV - A ROOT-based spectrum analysis software
 *  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
 *
 * This file is part of HDTV.
 *
 * HDTV is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * HDTV is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with HDTV; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
 * 
 */

#ifndef __MFileHist_h__
#define __MFileHist_h__

#ifndef __CINT__
#include <mfile.h>
#else
typedef unsigned int u_int;
#endif

#include <TH1.h>
#include <TH2.h>

//! Wrapper around the mfile library for reading spectra
class MFileHist {
  public:
    MFileHist();
    ~MFileHist();
    
    int Open(char *fname, char *fmt=NULL);
    int Close();
    
    inline int GetFileType()   { return fInfo ? fInfo->filetype : MAT_INVALID; }
    inline u_int GetNLevels()  { return fInfo ? fInfo->levels : 0; }
    inline u_int GetNLines()   { return fInfo ? fInfo->lines : 0; }
    inline u_int GetNColumns() { return fInfo ? fInfo->columns : 0; }
    
    double *FillBuf1D(double *buf, int level, int line);
    
    template <class histType>
    histType *ToTH1(const char *name, const char *title, int level, int line);
    
    TH1 *FillTH1(TH1 *hist, int level, int line);
    
    TH1D *ToTH1D(const char *name, const char *title, int level, int line);
	TH1I *ToTH1I(const char *name, const char *title, int level, int line);
	
	template <class histType>
    histType *ToTH2(const char *name, const char *title, int level);
    
    TH2 *FillTH2(TH2 *hist, int level);
    
    TH2D *ToTH2D(const char *name, const char *title, int level);
	TH2I *ToTH2I(const char *name, const char *title, int level);
	
	static int WriteTH1(const TH1 *hist, char *fname, char *fmt);
	static int WriteTH2(const TH2 *hist, char *fname, char *fmt);
	
	static const char *GetErrorMsg(int errno);
	inline const char *GetErrorMsg() { return GetErrorMsg(fErrno); }
	
	static const int ERR_SUCCESS;
	static const int ERR_READ_OPEN;
	static const int ERR_READ_INFO;
	static const int ERR_READ_NOTOPEN;
	static const int ERR_READ_BADIDX;
	static const int ERR_READ_GET;
	static const int ERR_READ_CLOSE;
	static const int ERR_WRITE_OPEN;
	static const int ERR_WRITE_INFO;
	static const int ERR_WRITE_PUT;
	static const int ERR_WRITE_CLOSE;
	static const int ERR_INVALID_FORMAT;
	static const int ERR_UNKNOWN;
    
  private:
#ifndef __CINT__
    MFILE *fHist;
    minfo *fInfo;
    int fErrno;
#endif
};

#endif
