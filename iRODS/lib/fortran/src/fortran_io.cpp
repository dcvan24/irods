/*
   irods fortran i/o library (initial version), somewhat based on the
   irods isio library (altho much simplier without the caching).

   This package provides a FORTRAN-callable set of functions to do
   irods IO (open, read, write, etc).

   The irods environment is assumed.  That is, like iCommands, this
   library needs to read the user's irods_environment.json and
   authentication files to be able to connect to an iRODS server.

   See ../test*.f90 files, and ../Makefile for more information.

 */

#include <stdio.h>
#include "rodsClient.h"
#include "dataObjRead.h"

int debug = 0;

static setupFlag = 0;

rcComm_t *Comm;
rodsEnv myRodsEnv;

int
irods_connect_() {
    int status;
    rErrMsg_t errMsg;

    if ( debug ) {
        printf( "irods_connect_\n" );
    }

    status = getRodsEnv( &myRodsEnv );
    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_connect_: getRodsEnv error." );
    }
    Comm = rcConnect( myRodsEnv.rodsHost, myRodsEnv.rodsPort,
                      myRodsEnv.rodsUserName,
                      myRodsEnv.rodsZone, 0, &errMsg );

    if ( Comm == NULL ) {
        char *mySubName = NULL;
        const char *myName = rodsErrorName( errMsg.status, &mySubName );
        rodsLog( LOG_ERROR, "rcConnect failure %s (%s) (%d) %s",
                 myName,
                 mySubName,
                 errMsg.status,
                 errMsg.msg );
        status = errMsg.status;
        free( mySubName );
        return status;
    }

    status = clientLogin( Comm );
    if ( status == 0 ) {
        setupFlag = 1;
    }
    return status;
}

int irods_file_open_( char *filename, char *mode ) {
    int i;
    int status;
    dataObjInp_t dataObjInp;
    char **outPath;
    char *cp1, *cp2;
    int nameLen;

    if ( debug ) {
        printf( "irods_file_open filename input:%s:\n", filename );
    }

    /* Remove trailing blanks from the filename */
    cp1 = filename;
    cp2 = cp1 + strlen( filename ) - 1;
    for ( ; *cp2 == ' ' && cp2 > cp1; cp2-- ) {
    }
    cp2++;
    if ( cp2 > cp1 ) {
        *cp2 = '\0';
    }

    if ( debug ) printf( "irods_file_open filename w/o trailing blanks:%s:\n",
                             filename );

    if ( setupFlag == 0 ) {
        status = irods_connect_();
        if ( status ) {
            return -1;
        }
    }

    memset( &dataObjInp, 0, sizeof( dataObjInp ) );
    status = parseRodsPathStr( filename , &myRodsEnv,
                               dataObjInp.objPath );
    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_file_open" );
        return -1;
    }

    /* Set the openFlags based on the input mode (incomplete
     * currently) // */
    dataObjInp.openFlags = O_RDONLY;
    if ( strstr( mode, "WRITE" ) != NULL ) {
        dataObjInp.openFlags = O_RDWR;
    }
    /* may want a O_WRONLY mode too sometime */

    status = rcDataObjOpen( Comm, &dataObjInp );

    if ( status == CAT_NO_ROWS_FOUND &&
            dataObjInp.openFlags == O_WRONLY ) {
        status = rcDataObjCreate( Comm, &dataObjInp );
    }
    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_file_open" );
        return -1;
    }
    return status;
}

int irods_file_create_( char *filename ) {
    int i;
    int status;
    dataObjInp_t dataObjInp;
    char **outPath;
    char *cp1, *cp2;
    int nameLen;

    if ( debug ) {
        printf( "irods_file_create filename input:%s:\n", filename );
    }

    /* Remove trailing blanks from the filename */
    cp1 = filename;
    cp2 = cp1 + strlen( filename ) - 1;
    for ( ; *cp2 == ' ' && cp2 > cp1; cp2-- ) {
    }
    cp2++;
    if ( cp2 > cp1 ) {
        *cp2 = '\0';
    }

    if ( debug ) printf( "irods_file_create filename w/o trailing blanks:%s:\n",
                             filename );

    if ( setupFlag == 0 ) {
        status = irods_connect_();
        if ( status ) {
            return -1;
        }
    }

    memset( &dataObjInp, 0, sizeof( dataObjInp ) );
    status = parseRodsPathStr( filename , &myRodsEnv,
                               dataObjInp.objPath );
    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_file_create" );
        return -1;
    }

    dataObjInp.openFlags = O_RDWR;
    /* may want a O_WRONLY mode too sometime */

    status = rcDataObjCreate( Comm, &dataObjInp );

    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_file_open" );
        return -1;
    }
    return status;
}

int irods_file_close_( int *fd ) {
    int status;
    openedDataObjInp_t dataObjCloseInp;

    if ( debug ) {
        printf( "irods_file_close fd: %d\n", *fd );
    }

    memset( &dataObjCloseInp, 0, sizeof( dataObjCloseInp ) );
    dataObjCloseInp.l1descInx = *fd;

    status = rcDataObjClose( Comm, &dataObjCloseInp );

    return status;
}

int
irods_file_read_( int *fd, void *buffer, int *size ) {
    openedDataObjInp_t dataObjReadInp;
    bytesBuf_t dataObjReadOutBBuf;
    int status;
    char *cp1;

    if ( debug ) {
        printf( "irods_file_read_\n" );
    }

    dataObjReadOutBBuf.buf = buffer;
    dataObjReadOutBBuf.len = *size;

    memset( &dataObjReadInp, 0, sizeof( dataObjReadInp ) );

    dataObjReadInp.l1descInx = *fd;
    dataObjReadInp.len = *size;

    status = rcDataObjRead( Comm, &dataObjReadInp,
                            &dataObjReadOutBBuf );

    if ( debug ) {
        printf( "irods_file_read_ rcDataObjRead stat: %d\n", status );
    }

    return status;
}

int
irods_file_write_( int *fd, void *buffer, int *size ) {
    openedDataObjInp_t dataObjWriteInp;
    bytesBuf_t dataObjWriteOutBBuf;
    int status;
    char *cp1;

    if ( debug ) {
        printf( "irods_file_write_\n" );
    }

    dataObjWriteOutBBuf.buf = buffer;
    dataObjWriteOutBBuf.len = *size;

    memset( &dataObjWriteInp, 0, sizeof( dataObjWriteInp ) );

    dataObjWriteInp.l1descInx = *fd;
    dataObjWriteInp.len = *size;

    status = rcDataObjWrite( Comm, &dataObjWriteInp,
                             &dataObjWriteOutBBuf );

    if ( debug ) {
        printf( "irods_file_write_ rcDataObjWrite stat: %d\n", status );
    }

    return status;
}

int
irods_file_seek_( int *fd, long *offset, char *whence ) {
    openedDataObjInp_t seekParam;
    fileLseekOut_t* seekResult = NULL;
    int status;
    int myWhence = 0;
    if ( strstr( whence, "SEEK_SET" ) != NULL ) {
        myWhence = SEEK_SET;
    }
    if ( strstr( whence, "SEEK_CUR" ) != NULL ) {
        myWhence = SEEK_CUR;
    }
    if ( strstr( whence, "SEEK_END" ) != NULL ) {
        myWhence = SEEK_END;
    }

    if ( debug ) {
        printf( "irods_file_seek_: %d\n", *fd );
    }
    memset( &seekParam,  0, sizeof( openedDataObjInp_t ) );
    seekParam.l1descInx = *fd;
    seekParam.offset  = *offset;
    seekParam.whence  = myWhence;
    status = rcDataObjLseek( Comm, &seekParam, &seekResult );
    if ( status < 0 ) {
        rodsLogError( LOG_ERROR, status, "irods_file_seek_" );
    }
    return status;
}

int
irods_disconnect_() {
    int status;
    if ( debug ) {
        printf( "irods_disconnect_" );
    }
    status = 0;
    if ( setupFlag > 0 ) {
        status = rcDisconnect( Comm );
    }
    return status;
}
