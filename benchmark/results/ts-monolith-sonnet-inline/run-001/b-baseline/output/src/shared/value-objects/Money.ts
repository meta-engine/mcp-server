import { Currency } from '../enums/Currency';

/** Represents a monetary amount with a currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
