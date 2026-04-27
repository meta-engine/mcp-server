import { Currency } from '../enums/Currency';

/** Monetary value with amount and currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
