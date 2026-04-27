import { Money } from "../../shared/value-objects/Money";

/** InvoiceLine value object. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
