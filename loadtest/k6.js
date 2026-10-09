
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE || 'http://localhost:8000';
const VUS = Number(__ENV.VUS || 1);
const HACKATHON_ID = Number(__ENV.HACKATHON_ID || 1);

export const options = {
  stages: [
    { duration: '10s', target: VUS },
    { duration: '30s', target: VUS },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<8000'],
  },
};

export default function () {
  const response = http.post(
    `${BASE_URL}/teams/generate`,
    JSON.stringify({
      hackathon_id: HACKATHON_ID,
      optimize_teams: true,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: '60s',
    },
  );

  check(response, {
    'team generation returned HTTP 200': (r) => r.status === 200,
  });

  sleep(1);
}
