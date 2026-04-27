import { Currency } from '../enums/Currency';

/** Money value object */
export interface Money {
  readonly amount: number;
  readonly currency: Currency;
}
