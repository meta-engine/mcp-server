import { Currency } from "../enums/Currency";

/** Monetary amount paired with a currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
