import { Currency } from '../enums/currency.enum';

/** Money value object. */
export interface Money {
  amount: number;
  currency: Currency;
}
