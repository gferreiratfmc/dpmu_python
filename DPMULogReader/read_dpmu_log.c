#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define NUMBER_OF_CELLS 30
//#define MAGIC_NUMBER 0x1234
#define MAGIC_NUMBER 0xDEADFACE


typedef struct debug_log
{
    uint32_t MagicNumber;
    int16_t ISen1;    // Output load current sensor x10
    int16_t ISen2;    // Storage current sensor (supercap) x10
    int16_t IF_1;     // Input current x10
    int16_t I_Dab2;   // CLLC1 Current x100
    int16_t I_Dab3;   // CLLC2 Current x100
    int16_t Vbus;      // VBus voltage x10
    int16_t VStore;    // VStore voltage x10
    int16_t AvgVbus;
    int16_t AvgVStore;
    int16_t BaseBoardTemperature;
    int16_t MainBoardTemperature;
    int16_t MezzanineBoardTemperature;
    int16_t PowerBankBoardTemperature;
    int16_t RegulateAvgInputCurrent;
    int16_t RegulateAvgOutputCurrent;
    int16_t RegulateAvgVStore;
    int16_t RegulateAvgVbus;
    int16_t RegulateIRef;
	uint16_t ILoop_PiOutput;
    int16_t cellVoltage[NUMBER_OF_CELLS];
    int16_t CurrentState; // State of CPU2 state machine
    uint16_t counter;
    uint32_t CurrentTime;
    uint16_t elapsed_time;	
} debug_log_t;




void log_debug_read_from_ram( debug_log_t dblog);
void print_buffer( unsigned char *buff);
void print_debug_log_raw(debug_log_t dblog);
void create_csv_line(char *csvLine, debug_log_t readBack);

debug_log_t dblog;
int count;
unsigned int initialCounter = 0, lastCounter = 0, MagicNumberCount = 0;

int main(int argc, char *argv[]) {
	
	char csvFileName[256];
	char csvLine[4096];
	char str[30];
	int file; 
	FILE *file_csv;
	uint32_t *MagicNumber;
	int ret;

	if( argc < 2) {
		printf("Use: %s fileName\r\n", argv[0]);
		return -1;
	} 

	sprintf(csvFileName, "%s.csv", argv[1]);
	file_csv = fopen( csvFileName,  "w+"  );	
	if( file_csv < 0) {
		printf("Erro arindo arquivo %s\r\n", csvFileName);		
		return -2;
	}
	printf("Output file csv: %s\r\n", csvFileName);

	file=open( argv[1], O_RDONLY );
	if(file < 0){
		printf("Erro arindo arquivo %s\r\n", argv[1]);
		return -2;
	}
	
	
	sprintf(csvLine, "%s", "VBus\tAvgVbus\tVStore\tAvgVStore\tInputCurrent\tOutputCurrent\tSupercapCurrent\tILoopPiOutput\tLLC1_Current\tLLC2_Current\tRegAvgVStore\tRegAvgVbus\tRegAvgInputCurrent\t"
						"RegAvgOutputCurrent\tRegIref\tTBase\tTMain\tTMezz\tTPWRBank\tCounter\tCurrentState\tElapsed_time\tTime");
	for(int i=0;i<30;i++) {
		sprintf(str, "\tCEL_%02d", i);
		strcat(csvLine, str);
	}
	strcat(csvLine, "\r\n\0");

	//printf("csvLine:%s\r\n", csvLine);
	fprintf(file_csv, "%s", csvLine );
	
	unsigned char buff[500];
	count = 0;
	int endOfFileReached=0;
	

	while(!endOfFileReached) {	

		memset(buff,0,sizeof(buff));
		ret = read( file, buff, sizeof(debug_log_t));
		if(ret < sizeof(debug_log_t) ) {
			endOfFileReached=1;			
			break;
		}

		int MagicNumberNotFound = 1;
		int ptr = 0;		
		while( MagicNumberNotFound && ptr < sizeof(debug_log_t) ) {
			MagicNumber=(uint32_t*)&buff[ptr];
			if( *MagicNumber == MAGIC_NUMBER ) {
				//printf("MAGIC NUMBER FOUND\r\n");
				MagicNumberCount++;
				MagicNumberNotFound = 0;				
			} else {
				ptr++;
			}			
		}

		if( ptr > 0 ) {
			if( ptr < sizeof(debug_log_t) ) {
				lseek( file, ptr, SEEK_CUR);
			}			
			continue;
		}
		
		memcpy(&dblog, buff, sizeof(debug_log_t) );	     
		if( dblog.MagicNumber != MAGIC_NUMBER ) {
			printf("Wrong magic number\r\n");
			break;
		}  
		lastCounter = dblog.counter;
		//print_buffer(buff);
		//print_debug_log_raw(dblog);
		//log_debug_read_from_ram(dblog);		
		if( initialCounter == 0){
			initialCounter = dblog.counter;
		}
		create_csv_line(csvLine, dblog);	
		//printf("%s", csvLine);
		fprintf(file_csv, "%s", csvLine );	
		count++;

	} 
	printf("Number of lines:[%u] - Initial counter:[%u] - Last counter:[%u] - Magic Number Count:[%d]\r\n",count, initialCounter, lastCounter, MagicNumberCount);
	close(file);
	fclose(file_csv);
	return 0;
}

void log_debug_read_from_ram(debug_log_t readBack)	{
		printf( "\r\nVoltages:\r\n");
        printf( "Vbus:[%03d] ", readBack.Vbus);
        printf( "AvgVbus:[%03d] ", readBack.AvgVbus);
        printf( "VStore:[%03d] ", readBack.VStore);
        printf( "AvgVStore:[%03d] ", readBack.AvgVStore);
        printf( "\r\nCurrents:\r\n");
        printf( "IF_1:[%03d] ", readBack.IF_1);
        printf( "ISen1:[%03d] ", readBack.ISen1);
        printf( "ISen2:[%03d] ", readBack.ISen2);
		printf( "ILoopPiOutput:[%03d] ", readBack.ILoop_PiOutput);
        printf( "I_Dab2:[%03d] ", readBack.I_Dab2);
        printf( "I_Dab3:[%03d]\r\n", readBack.I_Dab3);
        printf( "\r\nRegulate Vars:\r\n");
        printf( "AvgVstore:[%03d] ", readBack.RegulateAvgVStore);
        printf( "AvgVbus:[%03d] ", readBack.RegulateAvgVbus);
        printf( "AvgInputCurrent:[%03d] ", readBack.RegulateAvgInputCurrent);
        printf( "AvgOutpurCurrent:[%03d] ", readBack.RegulateAvgOutputCurrent);
        printf( "Iref:[%03d]\r\n", readBack.RegulateIRef);

        printf( "\r\nTemperatures:\r\n");
        printf( "Base:   [%02d] ", readBack.BaseBoardTemperature);
        printf( "Main:   [%02d] ", readBack.MainBoardTemperature);
        printf( "Mezz:   [%02d] ", readBack.MezzanineBoardTemperature);
        printf( "PWRBANK:[%02d] \r\n", readBack.PowerBankBoardTemperature);
        printf( "\r\nOthers:\r\n");
        printf( "Counter:     [%05d] ", readBack.counter);
        printf( "CurrentState:[%02d] ", readBack.CurrentState);
        printf( "Elapsed_time:[%08d] ", readBack.elapsed_time);
        printf( "Time:[%08u] \r\n", readBack.CurrentTime);

        printf( "\r\nCell Voltages:");
        printf( "\r\n");

        for(int c=0; c<NUMBER_OF_CELLS; c++){
            printf( "%2d:[%03d] ", c+1, readBack.cellVoltage[c]);
            if( (c+1) % 6 == 0 ) {
                printf( "\r\n");
            }
        }
        printf( "\r\n=============================\r\n");
}


void print_buffer( unsigned char *buff){
	for(int i=0;i<sizeof(debug_log_t);i++){
				printf("%02x ", buff[i]);
				if( (i+1)%4 == 0){
					printf("\r\n");
				}
			}		
}

void print_debug_log_raw(debug_log_t dblog){
		printf("ISen1:[0x%04X]\r\n",dblog.ISen1 );
		printf("ISen2:[0x%04X]\r\n",dblog.ISen2 );
		printf("IF_1:[0x%04X]\r\n",dblog.IF_1 );
		printf("I_Dab2:[0x%04X]\r\n",dblog.I_Dab2 );
		printf("I_Dab3:[0x%04X]\r\n",dblog.I_Dab3 );
		printf("Vbus:[0x%04X]\r\n",dblog.Vbus );
		printf("VStore:[0x%04X]\r\n",dblog.VStore );
		printf("AvgVbus:[0x%04X]\r\n",dblog.AvgVbus );
		printf("AvgVStore:[0x%04X]\r\n",dblog.AvgVStore );
		printf("BaseBoardTemperature:[0x%04X]\r\n",dblog.BaseBoardTemperature );
		printf("MainBoardTemperature:[0x%04X]\r\n",dblog.MainBoardTemperature );
		printf("MezzanineBoardTemperature:[0x%04X]\r\n",dblog.MezzanineBoardTemperature );
		printf("PowerBankBoardTemperature:[0x%04X]\r\n",dblog.PowerBankBoardTemperature );
		printf("RegulateAvgInputCurrent:[0x%04X]\r\n",dblog.RegulateAvgInputCurrent );
		printf("RegulateAvgOutputCurrent:[0x%04X]\r\n",dblog.RegulateAvgOutputCurrent );
		printf("RegulateAvgVStore:[0x%04X]\r\n",dblog.RegulateAvgVStore );
		printf("RegulateAvgVbus:[0x%04X]\r\n",dblog.RegulateAvgVbus );
		printf("RegulateIRef:[0x%04X]\r\n",dblog.RegulateIRef );
		for(int i=0;i<NUMBER_OF_CELLS;i++){
			printf("cv[%02d]:[0x%04X] ",i,dblog.cellVoltage[i] );
			if(i+1%6==0){
				printf("\r\n");
			}
		}
		printf("CurrentState:[0x%04X]\r\n",dblog.CurrentState ); // State of CPU2 state machine
		printf("counter:[0x%04X]\r\n",dblog.counter );
		printf("CurrentTime:[0x%08X]\r\n",dblog.CurrentTime );
		printf("elapsed_time:[0x%04X]\r\n",dblog.elapsed_time );
			
		
		printf("=========== Count:[%03d] ==============\r\n", count++);
}

void create_csv_line(char *csvLine, debug_log_t readBack) {
	char str[100];
	memset( csvLine, '\0', 4096);
	sprintf( str, "%6.2f\t", (float)readBack.Vbus/10);                                strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.AvgVbus/10);                             strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.VStore/10);                              strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.AvgVStore/10);                           strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.IF_1/10);                                strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.ISen1/10);                               strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.ISen2/10);                               strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.ILoop_PiOutput/100);                     strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.I_Dab2/100);                             strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.I_Dab3/100);                             strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.RegulateAvgVStore/10);                   strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.RegulateAvgVbus/10);                     strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.RegulateAvgInputCurrent/10);             strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.RegulateAvgOutputCurrent/10);            strcat( csvLine, str);
	sprintf( str, "%6.2f\t", (float)readBack.RegulateIRef/100);                       strcat( csvLine, str);
	sprintf( str, "%02d\t", readBack.BaseBoardTemperature);                           strcat( csvLine, str);
	sprintf( str, "%02d\t", readBack.MainBoardTemperature);                           strcat( csvLine, str);
	sprintf( str, "%02d\t", readBack.MezzanineBoardTemperature);                      strcat( csvLine, str);
	sprintf( str, "%02d\t", readBack.PowerBankBoardTemperature);                      strcat( csvLine, str);
	sprintf( str, "%05d\t", readBack.counter);                                        strcat( csvLine, str);
	sprintf( str, "%02d\t", readBack.CurrentState);                                   strcat( csvLine, str);
	sprintf( str, "%08d\t", readBack.elapsed_time);                                   strcat( csvLine, str);
	sprintf( str, "%08u", readBack.CurrentTime);                                    strcat( csvLine, str);
	for(int c=0; c<NUMBER_OF_CELLS; c++){
		sprintf( str, "\t%6.2f", (float)readBack.cellVoltage[c]/100);   
		strcat( csvLine, str);
	}
	strcat( csvLine, "\r\n");
}