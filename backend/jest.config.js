export default {
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { 
      useESM: true
    }]
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'mjs'],
  testMatch: ['**/tests/unit/config.test.js', '**/tests/unit/middleware.test.js'],
  collectCoverageFrom: ['src/**/*.ts', 'src/**/*.js'],
  coverageDirectory: 'coverage',
  verbose: true,
  testTimeout: 10000
};
