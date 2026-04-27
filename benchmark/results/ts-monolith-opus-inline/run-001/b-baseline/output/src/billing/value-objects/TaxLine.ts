import { Money } from "../../shared/value-objects/Money";

/** Tax component applied to an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
