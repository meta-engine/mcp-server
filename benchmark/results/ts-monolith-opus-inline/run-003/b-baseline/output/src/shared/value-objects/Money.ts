import { Currency } from "../enums/Currency";

/** Money value object: amount with currency. */
export interface Money {
  amount: number;
  currency: Currency;
}
