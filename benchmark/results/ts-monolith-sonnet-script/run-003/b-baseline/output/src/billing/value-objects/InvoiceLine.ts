import { Money } from '../../shared/value-objects/Money';

/** InvoiceLine value object */
export interface InvoiceLine {
  readonly description: string;
  readonly amount: Money;
}
