import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** Customer payment instrument on file. */
export interface PaymentMethod {
  kind: PaymentMethodKind;
  lastFour: string;
}
