#include <avr/io.h>
#include "UART.h"
volatile uint8_t data = 0;
volatile unsigned char leituraL;
volatile unsigned char leituraH;
volatile long unsigned int temperatura;
volatile byte temp;

void init(void);
void ler_temperatura(void);
int ler_ad(void);

/**********************   Inicializacoes **********************/
void init(void)
{
// Configuracao da saída do relé   
  DDRB=(1<<PB4);        // Configura o relé como saída
  PORTB=(0<<PB4);       // Pull up desativada

// Configuracao do Conversor AD
  ADMUX=(0<<ADLAR)|(1<<REFS0)|(0<<MUX0);  // Resultado ajustado e esquerda e uso do PA0
  ADCSRA=(1<<ADEN)|(1<<ADPS2)|(1<<ADPS1); 
  ADCSRB=0;                               // Free Running Mode
                              // Free Running Mode
}

/**********************   Interrupcao do USART **********************/
ISR(USART_RX_vect)
{
    data = UART_read();
}

/**********************     Ler Temperatura    **********************/
void ler_temperatura(void)
{
  temperatura = ler_ad();           // Vamos buscar o valor da conversao AD
  temperatura = temperatura*5*100;  // Multiplicamos o valor do ADC por 5 e por 100
  temp = temperatura/1024;   // Dividimos por 1024 porque a resolucao e de 10 bits

  UART_write_temp(temp);
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
    init();
    UART_init();
    sei();

    while(1)
    {
        if(data != 0 )
        {
            switch (data)
            {
            case 'D':
                PORTB = (0<<PB4);
                break;
            
            case 'L':
                PORTB = (1<<PB4);
                break;

            case 'T':
                ler_temperatura();
                break;
            
            default:
                break;
            }
            data = 0;
        }
    }
}
