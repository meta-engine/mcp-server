import { Currency } from '../enums/Currency';

/** Money value object. */
export interface Money {
  amount: number;
  currency: Currency;
}
