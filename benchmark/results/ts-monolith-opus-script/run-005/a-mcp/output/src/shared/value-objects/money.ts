import { Currency } from '../enums/currency.enum';

export interface Money {
  amount: number;
  currency: Currency;
}
