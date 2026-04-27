import { Currency } from '../enums/Currency';

/** Money value object representing an amount in a given currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
