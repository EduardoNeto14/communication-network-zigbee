#include <XBee.h>
#include<avr/io.h>
#include "UART.h"
#include <util/delay.h>

XBee xbee = XBee();
XBeeResponse response = XBeeResponse();
ZBRxResponse rx = ZBRxResponse();
XBeeAddress64 addr64 = XBeeAddress64(0x00000000, 0x00000000);
uint8_t payload[] = { 0 };
ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));

volatile uint8_t data=0;
volatile unsigned char leituraL;
volatile unsigned char leituraH;
volatile long unsigned int temperatura;
volatile byte temp;

void inicializacao(void);
void ler_temperatura(void);
int ler_ad(void);

/**********************   Inicializacoes **********************/
void inicializacao(void)
{
  // Configuracao da saída do relé e LED  
  DDRB=(1<<PB4)|(1<<PB5);        // Configura o relé e LED como saída
  PORTB=(1<<PB4)|(0<<PB5);       // Pull up desativada

// Configuracao do Conversor AD
  ADMUX=(0<<ADLAR)|(1<<REFS0)|(0<<MUX0);  // Resultado ajustado e esquerda e uso do PA0
  ADCSRA=(1<<ADEN)|(1<<ADPS2)|(1<<ADPS1); // Enable do ADC e sua interrupcao; Prescaler = 8 -> fclk interna = 1Mhz/8 = 125khz, situada entre 50 e 200khz
  ADCSRB=0;                               // Free Running Mode
  
// Inicializacao em serie
  Serial.begin(9600);
  xbee.begin(Serial);
  
}

/**********************     Ler Temperatura    **********************/
void ler_temperatura(void)
{
  temperatura = ler_ad();           // Vamos buscar o valor da conversao AD
  temperatura = temperatura*5*100;  // Multiplicamos o valor do ADC por 5 e por 100
  temp = temperatura/1024;          // Dividimos por 1024 porque a resolucao e de 10 bits
  
  payload[0]=temp;
  xbee.send(zbTx);
  //UART_write_temp(temp);
}

/**********************   Conversao da Temperatura **********************/
int ler_ad(void)
{
  ADCSRA= ADCSRA|0b01000000;        // (ADSC=1) realiza a operacao OR
  while ((ADCSRA & (1<<ADSC))!=0);  // Aguardar que ADCS seja 0 para terminar a conversao
  leituraL=ADCL;                    // Igualamos o valor da temperatura a ADCL para obtermos um valor mais aproximado da conversao
  leituraH=ADCH;                    // Igualamos o valor da temperatura a ADCH para obtermos um valor mais aproximado da conversao
  
  return ((leituraH<<8)+leituraL);
}

/***********************************************************************/
/******************************   Main    ******************************/
/***********************************************************************/
int main(void)
{
    inicializacao();
    //UART_init();
    sei();

    while(1)
    {
        xbee.readPacket();
        
        if (xbee.getResponse().isAvailable())
        {  // got something
          
            if (xbee.getResponse().getApiId() == ZB_RX_RESPONSE)
            {
              // Rececao do pacote rx por zigbee
              // Insercao do pacote recebido na estrutura rx
              xbee.getResponse().getZBRxResponse(rx);
    
              // Analise de dados
              data = rx.getData(0);
              if(data=='D')
                {
                PORTB = (1<<PB4)|(0<<PB5);
                }
                
              else if(data=='L')
                {
                PORTB = (0<<PB4)|(1<<PB5);
                }
              else if(data=='T')
                {
                ler_temperatura();
                }
              
              // Verificacao do pacote ACK
              if (rx.getOption() == ZB_PACKET_ACKNOWLEDGED)
              {
//                  PORTB = (1<<PB5);
//                  _delay_ms(100);
//                  PORTB = (0<<PB5);
              }
            
              else
              {
//                  PORTB = (1<<PB5);
              }
            }
        }
        
        else if (xbee.getResponse().isError())
        {
          //nss.print("Error reading packet.  Error code: ");  
          //nss.println(xbee.getResponse().getErrorCode());
        }
    }
}
