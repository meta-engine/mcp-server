import { Currency } from "../enums/Currency";

/** Monetary amount paired with its currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
