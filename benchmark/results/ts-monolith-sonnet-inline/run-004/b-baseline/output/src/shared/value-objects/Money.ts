import { Currency } from '../enums/Currency';

/** Monetary amount with currency denomination */
export interface Money {
  amount: number;
  currency: Currency;
}
