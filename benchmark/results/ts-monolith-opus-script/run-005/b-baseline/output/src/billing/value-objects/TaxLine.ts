import { Money } from "../../shared/value-objects/Money";

/** A tax line on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
