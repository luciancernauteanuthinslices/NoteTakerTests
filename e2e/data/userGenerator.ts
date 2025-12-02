import { faker } from '@faker-js/faker';

export interface GeneratedUser {
  email: string;
  name: string;
  password: string;
}

/**
 * Generates a new user with random credentials using Faker.
 * Password meets typical requirements (6-30 chars).
 */
export function generateUser(): GeneratedUser {
  const firstName = faker.person.firstName();
  const lastName = faker.person.lastName();
  const name = `${firstName} ${lastName}`;
  
  // Generate unique email with timestamp to avoid collisions
  const timestamp = Date.now();
  const email = faker.internet.email({
    firstName,
    lastName,
    provider: `test${timestamp}.example.com`,
  }).toLowerCase();
  
  // Generate password (8-20 chars, alphanumeric)
  const password = faker.internet.password({ length: 12, memorable: false });
  
  return {
    email,
    name,
    password,
  };
}

/**
 * Generates user credentials and returns them along with confirmPassword.
 * Useful for registration forms.
 */
export function generateRegistrationData() {
  const user = generateUser();
  return {
    ...user,
    confirmPassword: user.password,
  };
}
