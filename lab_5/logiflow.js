import http from 'k6/http';
import { check, group, sleep } from 'k6';

const api = __ENV.BASE_URL || 'http://localhost/api/v1';
const scenario = (__ENV.SCENARIO || 'read').toLowerCase();
const duration = __ENV.STAGE_DURATION || '30s';
const summaryFile = __ENV.SUMMARY_FILE || `results/${scenario}-summary.json`;
const fixedVus = Number(__ENV.FIXED_VUS || 0);
let authenticated = false;
let readScenarioOrderId = null;
let accessToken = null;

export const options = {
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  ...(fixedVus > 0
    ? { vus: fixedVus, duration }
    : {
        stages: [
          { duration: '30s', target: 10 },
          { duration, target: 25 },
          { duration, target: 50 },
          { duration, target: 100 },
          { duration, target: 200 },
          { duration: '30s', target: 0 },
        ],
      }),
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    checks: ['rate>0.98'],
  },
};

function uniqueIdentity() {
  const suffix = `${Date.now()}-${Math.floor(Math.random() * 1000000000)}`;
  const phoneSuffix = String(Math.floor(Math.random() * 100000000)).padStart(8, '0');
  return {
    email: `load-${suffix}@example.com`,
    password: __ENV.TEST_PASSWORD || 'LoadTestPassword123!',
    full_name: `Load Test VU ${__VU}`,
    role: 'client',
    phone_number: `+38099${phoneSuffix}`.slice(-13),
  };
}

function jsonParams() {
  const params = { headers: { 'Content-Type': 'application/json' } };
  if (accessToken) params.cookies = { access_token: accessToken };
  return params;
}

function requestParams() {
  return accessToken ? { cookies: { access_token: accessToken } } : {};
}

function valid(response, expectedStatus, label) {
  return check(response, {
    [`${label}: status ${expectedStatus}`]: (item) => item.status === expectedStatus,
  });
}

function login(credentials) {
  const response = http.post(`${api}/auth/login`, JSON.stringify({
    email: credentials.email,
    password: credentials.password,
  }), jsonParams());
  const passed = valid(response, 200, 'login');
  if (passed && response.cookies.access_token) {
    accessToken = response.cookies.access_token[0].value;
  }
  return passed;
}

function createOrder() {
  const response = http.post(`${api}/orders/`, JSON.stringify({
    title: `Load order ${__VU}-${__ITER}`,
    description: 'Declarative k6 load-test order',
    origin_address: 'Kyiv, Khreshchatyk 1',
    destination_address: 'Lviv, Zelena 10',
    weight: 10,
    total_amount: 1500,
    distance: 120,
    is_template: false,
  }), jsonParams());
  valid(response, 201, 'create order');
  if (response.status !== 201) return null;
  return response.json('id');
}

function readOrder(orderId, label = 'read order') {
  const response = http.get(`${api}/orders/${orderId}`, requestParams());
  valid(response, 200, label);
  return response;
}

function updateOrder(orderId) {
  const response = http.patch(`${api}/orders/${orderId}`, JSON.stringify({
    title: `Updated load order ${__VU}-${__ITER}`,
  }), jsonParams());
  return valid(response, 200, 'update order');
}

export function setup() {
  const credentials = uniqueIdentity();
  const registration = http.post(`${api}/auth/register`, JSON.stringify(credentials), jsonParams());
  valid(registration, 201, 'register');
  return credentials;
}

export default function (credentials) {
  if (!authenticated && !login(credentials)) {
    sleep(1);
    return;
  }
  authenticated = true;

  let orderId = null;
  group('business scenario', () => {
    if (scenario === 'read') {
      if (!readScenarioOrderId) {
        readScenarioOrderId = createOrder();
      }
      if (readScenarioOrderId) {
        readOrder(readScenarioOrderId, 'read-intensive detail');
        readOrder(readScenarioOrderId, 'read-intensive detail repeat');
      }
    } else if (scenario === 'write') {
      createOrder();
    } else if (scenario === 'workflow') {
      orderId = createOrder();
      if (orderId) {
        readOrder(orderId, 'workflow initial read');
        updateOrder(orderId);
        readOrder(orderId, 'workflow consistency read');
      }
    } else {
      throw new Error(`Unsupported SCENARIO=${scenario}; use read, write, or workflow`);
    }
  });
  sleep(0.2);
}

export function handleSummary(data) {
  return { [summaryFile]: JSON.stringify(data, null, 2) };
}
