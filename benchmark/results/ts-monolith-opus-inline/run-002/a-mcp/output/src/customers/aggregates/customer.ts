import { Id } from '../../shared/value-objects/id';
import { Email } from '../value-objects/email';
import { CustomerStatus } from '../enums/customer-status.enum';
import { Timestamp } from '../../shared/value-objects/timestamp';

/** Customer aggregate root for the customers module. */
export class Customer {

  constructor(public id: Id, public email: Email, public status: CustomerStatus, public createdAt: Timestamp) { }
}
