#include <bur/plctypes.h>  
#ifdef _DEFAULT_INCLUDES 
#include <AsDefault.h> 
#endif 
#include <RtkUser.h> 

RTK_ERROR statusStopThread; 
RTK_ERROR statusStartThread; 

void incr_a(USINT* par) 
{ 
 	while(1){ 
 		cnt_a++; 
 		if((cnt_a&0xFF)==128){ 
 	(*par)=1; 
 	RtkWritePlainFifo (FIFOIdent, par); 
 	}else 
 		(*par)=0; 
 	} 
}

USINT fifo_rd; 

void incr_b(USINT* par) 
{ 
 	while(1) 
 	{ 
 	if ((*par)==1) 
 		cnt_c=cnt_c+256; 
 	while ( (RtkReadPlainFifo(FIFOIdent,&fifo_rd)==0)){ 
 		cnt_b=cnt_b+fifo_rd*256; 
 	} 
 	RtkSleepTaskUsec(1); 
 	} 
} 
 
void _INIT NewProgramInit(void) 
{ 
 
} 
 
 
void _CYCLIC NewProgramCyclic(void) 
{ 
 if(StopThread) 
 { 
 StopThread = 0; 
 statusStopThread = RtkDeleteTask(TaskIdentA); 
 statusStopThread = RtkDeleteTask(TaskIdentB); 
 RtkDeletePlainFifo(FIFOIdent); 
 cnt_a = 0; 
 cnt_b = 0; 
 cnt_c = 0;
 }
 if(StartThread) 
 { 
 cnt_a = 0; 
 cnt_b = 0; 
 cnt_c = 0; 
 StartThread = 0; 
 RtkCreatePlainFifo ( "ABFIFO", 1, 1024, &FIFOIdent); 
 statusStartThread = RtkCreateTask ( 
 
 "TestTaskA", // LPSTRING lpszTaskName, 
 10, 
// WORD wTaskPriority, 
 8192, 
// ULONG ulTaskSupervisorStackSize, 
 8192, 
// ULONG ulTaskUserStackSize, 
 
 RTK_TASK_APPLICATION, // RTK_TASKFLAG TaskFlags, 
 (void*) 
incr_a,         // LPRTK_CREATE_TASK_FKT lpTaskFunction, 
 (ULONG) 
&a,             // ULONG ulTaskFunctionParameter, 
 
 &TaskIdentA // LPULONG lpulTaskIdent 
 ); 
 statusStartThread = RtkCreateTask ( 
 
 "TestTaskB", // LPSTRING lpszTaskName, 
 10, 
// WORD wTaskPriority, 
 8192, 
// ULONG ulTaskSupervisorStackSize, 
 8192, 
// ULONG ulTaskUserStackSize, 
 
 RTK_TASK_APPLICATION, // RTK_TASKFLAG TaskFlags, 
 (void*) 
incr_b,         // LPRTK_CREATE_TASK_FKT lpTaskFunction, 
 (ULONG) 
&a,             // ULONG ulTaskFunctionParameter 
 
 &TaskIdentB // LPULONG lpulTaskIdent 
 ); 
 } 
} 