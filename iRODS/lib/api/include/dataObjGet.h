/*** Copyright (c), The Regents of the University of California            ***
 *** For more information please refer to files in the COPYRIGHT directory ***/
/* dataObjGet.h - This dataObj may be generated by a program or script
 */

#ifndef DATA_OBJ_GET_H__
#define DATA_OBJ_GET_H__

/* This is a high level type API call */

#include "rcConnect.h"
#include "rodsDef.h"
#include "dataObjInpOut.h"

#if defined(RODS_SERVER)
#define RS_DATA_OBJ_GET rsDataObjGet
/* prototype for the server handler */
int
rsDataObjGet( rsComm_t *rsComm, dataObjInp_t *dataObjInp,
              portalOprOut_t **portalOprOut, bytesBuf_t *dataObjOutBBuf );
int
_rsDataObjGet( rsComm_t *rsComm, dataObjInp_t *dataObjInp,
               portalOprOut_t **portalOprOut, bytesBuf_t *dataObjOutBBuf, int handlerFlag, dataObjInfo_t *dataObjInfoHead );
int
preProcParaGet( rsComm_t *rsComm, int l1descInx,
                portalOprOut_t **portalOprOut );
int
l3DataGetSingleBuf( rsComm_t *rsComm, int l1descInx,
                    bytesBuf_t *dataObjOutBBuf, portalOprOut_t **portalOprOut );
int
l3FileGetSingleBuf( rsComm_t *rsComm, int l1descInx,
                    bytesBuf_t *dataObjOutBBuf );
#else
#define RS_DATA_OBJ_GET NULL
#endif

#ifdef __cplusplus
extern "C" {
#endif
/* prototype for the client call */
/* rcDataObjGet - Get (download) a iRODS data object.
 * Input -
 *   rcComm_t *conn - The client connection handle.
 *   dataObjInp_t *dataObjInp - generic dataObj input. Relevant items are:
 *      objPath - the path of the data object.
 *      numThreads - Number of threads to use. NO_THREADING ==> no threading,
 *         0 ==> server will decide (default), >0 ==> number of threads.
 *      openFlags - should be set to O_RDONLY.
 *      condInput - conditional Input
 *          FORCE_FLAG_KW - overwrite an existing data object
 *          REPL_NUM_KW  - "value" = The replica number of the copy to
 *              download.
 *          VERIFY_CHKSUM_KW - verify the checksum of the download file.
 *   return value - The status of the operation.
 */
int
rcDataObjGet( rcComm_t *conn, dataObjInp_t *dataObjInp, char *locFilePath, int localPort);

int
_rcDataObjGet( rcComm_t *conn, dataObjInp_t *dataObjInp,
               portalOprOut_t **portalOprOut, bytesBuf_t *dataObjOutBBuf );

#ifdef __cplusplus
}
#endif
#endif  // DATA_OBJ_GET_H__
