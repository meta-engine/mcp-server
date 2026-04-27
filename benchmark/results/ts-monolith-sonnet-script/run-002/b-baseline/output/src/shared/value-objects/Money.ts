import { Currency } from '../enums/Currency';

/** Monetary amount with an associated currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
