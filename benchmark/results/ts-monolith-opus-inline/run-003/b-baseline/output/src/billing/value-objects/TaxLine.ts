import { Money } from "../../shared/value-objects/Money";

/** Tax line on an Invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
