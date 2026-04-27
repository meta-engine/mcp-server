import { Currency } from '../enums/Currency';

/** Monetary amount with currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
