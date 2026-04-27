import { Money } from "../../shared/value-objects/Money";

/** Single tax line on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
