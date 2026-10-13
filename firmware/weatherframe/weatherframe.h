// Weather frame: Open-Meteo parsing, deep-sleep-persistent cache and 800x480 layout.
// Shared by the device firmware (weatherframe.yaml) and the Mac preview (preview.yaml).
#pragma once

#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <ctime>

#include "esphome/core/log.h"
#include "esphome/components/display/display.h"
#include "esphome/components/json/json_util.h"

#ifdef USE_ESP32
#include "esp_attr.h"
#define WF_RTC RTC_DATA_ATTR
#else
#define WF_RTC
#endif

namespace wf {

using esphome::Color;
using esphome::display::BaseFont;
using esphome::display::Display;
using esphome::display::TextAlign;

static const char *const TAG = "weatherframe";

static const Color BLACK(0, 0, 0);
static const Color WHITE(255, 255, 255);

static const int W = 800;
static const int H = 480;
static const int HOURS = 24;
static const int DAYS = 6;  // today + 5
static const uint32_t MAGIC = 0x57465231;  // "WFR1"

// ---------------------------------------------------------------------------
// Cache: lives in RTC slow memory, survives deep sleep (not power loss).
// ---------------------------------------------------------------------------
struct Cache {
  uint32_t magic;
  int64_t fetched;     // unix time of last successful fetch
  int32_t utc_offset;  // seconds, from Open-Meteo (timezone=auto)
  float temp, feels, wind, humidity;
  int16_t code;
  bool is_day;
  int64_t hour0;  // unix time of first hourly slot
  float h_temp[HOURS];
  uint8_t h_pop[HOURS];
  int16_t h_code[HOURS];
  int64_t d_time[DAYS];
  int16_t d_code[DAYS];
  float d_max[DAYS], d_min[DAYS], d_rain[DAYS];
  uint8_t d_pop[DAYS];
  int64_t sunrise, sunset;
};

WF_RTC static Cache cache;

inline bool have_data() { return cache.magic == MAGIC; }

// ---------------------------------------------------------------------------
// Open-Meteo
// ---------------------------------------------------------------------------
inline std::string build_url(float lat, float lon, bool fahrenheit) {
  char buf[640];
  snprintf(buf, sizeof(buf),
           "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f"
           "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,is_day"
           "&hourly=temperature_2m,precipitation_probability,weather_code"
           "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
           "precipitation_probability_max,sunrise,sunset"
           "&timezone=auto&forecast_days=%d&forecast_hours=%d&timeformat=unixtime%s",
           lat, lon, DAYS, HOURS, fahrenheit ? "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch" : "");
  return buf;
}

// Parses an Open-Meteo response into the cache. Returns false (cache untouched) on error.
inline bool parse(const std::string &body) {
  Cache c{};
  bool ok = esphome::json::parse_json(body, [&c](JsonObject root) -> bool {
    if (!root["current"].is<JsonObject>() || !root["hourly"].is<JsonObject>() || !root["daily"].is<JsonObject>())
      return false;
    c.utc_offset = root["utc_offset_seconds"] | 0;
    JsonObject cur = root["current"];
    c.temp = cur["temperature_2m"] | NAN;
    c.feels = cur["apparent_temperature"] | NAN;
    c.wind = cur["wind_speed_10m"] | NAN;
    c.humidity = cur["relative_humidity_2m"] | NAN;
    c.code = cur["weather_code"] | 0;
    c.is_day = (cur["is_day"] | 1) != 0;

    JsonObject hr = root["hourly"];
    JsonArray ht = hr["time"], htemp = hr["temperature_2m"], hpop = hr["precipitation_probability"],
              hcode = hr["weather_code"];
    if (ht.size() < HOURS || htemp.size() < HOURS)
      return false;
    c.hour0 = ht[0] | (int64_t) 0;
    for (int i = 0; i < HOURS; i++) {
      c.h_temp[i] = htemp[i] | NAN;
      c.h_pop[i] = hpop[i] | 0;
      c.h_code[i] = hcode[i] | 0;
    }

    JsonObject d = root["daily"];
    JsonArray dt = d["time"];
    if (dt.size() < DAYS)
      return false;
    for (int i = 0; i < DAYS; i++) {
      c.d_time[i] = dt[i] | (int64_t) 0;
      c.d_code[i] = d["weather_code"][i] | 0;
      c.d_max[i] = d["temperature_2m_max"][i] | NAN;
      c.d_min[i] = d["temperature_2m_min"][i] | NAN;
      c.d_rain[i] = d["precipitation_sum"][i] | 0.0f;
      c.d_pop[i] = d["precipitation_probability_max"][i] | 0;
    }
    c.sunrise = d["sunrise"][0] | (int64_t) 0;
    c.sunset = d["sunset"][0] | (int64_t) 0;
    return true;
  });
  if (!ok) {
    ESP_LOGW(TAG, "Open-Meteo response could not be parsed (%u bytes)", (unsigned) body.size());
    return false;
  }
  c.magic = MAGIC;
  cache = c;
  ESP_LOGI(TAG, "Weather: %.1f° code %d, %d hourly / %d daily slots", c.temp, c.code, HOURS, DAYS);
  return true;
}

inline void set_fetched(int64_t now) { cache.fetched = now; }

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// UTF-8 encode a code point (MDI icons live in the U+F0000 plane).
inline std::string u8(uint32_t cp) {
  char s[5] = {0};
  if (cp < 0x80) {
    s[0] = cp;
  } else if (cp < 0x800) {
    s[0] = 0xC0 | (cp >> 6);
    s[1] = 0x80 | (cp & 0x3F);
  } else if (cp < 0x10000) {
    s[0] = 0xE0 | (cp >> 12);
    s[1] = 0x80 | ((cp >> 6) & 0x3F);
    s[2] = 0x80 | (cp & 0x3F);
  } else {
    s[0] = 0xF0 | (cp >> 18);
    s[1] = 0x80 | ((cp >> 12) & 0x3F);
    s[2] = 0x80 | ((cp >> 6) & 0x3F);
    s[3] = 0x80 | (cp & 0x3F);
  }
  return s;
}

namespace icon {
static const uint32_t SUNNY = 0xF0599, NIGHT = 0xF0594, PARTLY = 0xF0595, NIGHT_PARTLY = 0xF0F31, CLOUDY = 0xF0590,
                      FOG = 0xF0591, HAIL = 0xF0592, LIGHTNING = 0xF0593, LIGHTNING_RAINY = 0xF067E,
                      POURING = 0xF0596, RAINY = 0xF0597, PARTLY_RAINY = 0xF0F33, SNOWY = 0xF0598,
                      SNOWY_HEAVY = 0xF0F36, SNOWY_RAINY = 0xF067F, SUNRISE = 0xF059C, SUNSET = 0xF059B,
                      HOME_THERMO = 0xF0F55, WATER = 0xF058E, WIND = 0xF059D, UMBRELLA = 0xF054B, WIFI_OFF = 0xF05AA,
                      BATTERY_ALERT = 0xF0083, BATTERY_CHARGING = 0xF0084, THERMO = 0xF050F;
}  // namespace icon

// WMO weather code -> MDI icon.
inline uint32_t code_icon(int code, bool day = true) {
  switch (code) {
    case 0:
      return day ? icon::SUNNY : icon::NIGHT;
    case 1:
    case 2:
      return day ? icon::PARTLY : icon::NIGHT_PARTLY;
    case 3:
      return icon::CLOUDY;
    case 45:
    case 48:
      return icon::FOG;
    case 51:
    case 53:
    case 55:
    case 80:
      return icon::PARTLY_RAINY;
    case 56:
    case 57:
    case 66:
    case 67:
      return icon::SNOWY_RAINY;
    case 61:
    case 63:
    case 81:
      return icon::RAINY;
    case 65:
    case 82:
      return icon::POURING;
    case 71:
    case 73:
    case 77:
    case 85:
      return icon::SNOWY;
    case 75:
    case 86:
      return icon::SNOWY_HEAVY;
    case 95:
      return icon::LIGHTNING_RAINY;
    case 96:
    case 99:
      return icon::HAIL;
    default:
      return icon::CLOUDY;
  }
}

inline const char *code_text(int code, bool de) {
  switch (code) {
    case 0:
      return de ? "Klar" : "Clear";
    case 1:
      return de ? "Überwiegend klar" : "Mainly clear";
    case 2:
      return de ? "Teilweise bewölkt" : "Partly cloudy";
    case 3:
      return de ? "Bedeckt" : "Overcast";
    case 45:
    case 48:
      return de ? "Nebel" : "Fog";
    case 51:
    case 53:
    case 55:
      return de ? "Nieselregen" : "Drizzle";
    case 56:
    case 57:
      return de ? "Gefrierender Niesel" : "Freezing drizzle";
    case 61:
      return de ? "Leichter Regen" : "Light rain";
    case 63:
      return de ? "Regen" : "Rain";
    case 65:
      return de ? "Starker Regen" : "Heavy rain";
    case 66:
    case 67:
      return de ? "Gefrierender Regen" : "Freezing rain";
    case 71:
      return de ? "Leichter Schnee" : "Light snow";
    case 73:
      return de ? "Schnee" : "Snow";
    case 75:
      return de ? "Starker Schnee" : "Heavy snow";
    case 77:
      return de ? "Schneegriesel" : "Snow grains";
    case 80:
    case 81:
      return de ? "Regenschauer" : "Rain showers";
    case 82:
      return de ? "Heftige Schauer" : "Violent showers";
    case 85:
    case 86:
      return de ? "Schneeschauer" : "Snow showers";
    case 95:
      return de ? "Gewitter" : "Thunderstorm";
    case 96:
    case 99:
      return de ? "Gewitter mit Hagel" : "Thunderstorm, hail";
    default:
      return "?";
  }
}

inline struct tm local_tm(int64_t t, int32_t offset) {
  time_t lt = (time_t) (t + offset);
  struct tm out;
  gmtime_r(&lt, &out);
  return out;
}

inline const char *weekday(int wday, bool de, bool longname = false) {
  static const char *en_s[] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
  static const char *de_s[] = {"So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"};
  static const char *en_l[] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
  static const char *de_l[] = {"Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"};
  return longname ? (de ? de_l : en_l)[wday] : (de ? de_s : en_s)[wday];
}

inline const char *month(int mon, bool de) {
  static const char *en[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
  static const char *de_m[] = {"Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."};
  return (de ? de_m : en)[mon];
}

// Single-cell LiPo open-circuit voltage -> percent (piecewise linear).
inline int battery_percent(float v) {
  static const float tbl[][2] = {{4.20f, 100}, {4.10f, 90}, {4.00f, 80}, {3.90f, 68}, {3.80f, 55}, {3.75f, 45},
                                 {3.70f, 35},  {3.65f, 25}, {3.60f, 17}, {3.50f, 8},  {3.40f, 3},  {3.30f, 0}};
  if (std::isnan(v))
    return -1;
  if (v >= tbl[0][0])
    return 100;
  for (unsigned i = 1; i < sizeof(tbl) / sizeof(tbl[0]); i++) {
    if (v >= tbl[i][0]) {
      float f = (v - tbl[i][0]) / (tbl[i - 1][0] - tbl[i][0]);
      return (int) lroundf(tbl[i][1] + f * (tbl[i - 1][1] - tbl[i][1]));
    }
  }
  return 0;
}

// Milliseconds until the next wake: aligned to the next `interval_s` boundary (local time),
// pushed to the end of quiet hours [quiet_start, quiet_end) if that boundary falls inside them.
// quiet_start == quiet_end disables quiet hours. now == 0 (time unknown) -> plain interval.
inline uint32_t next_sleep_ms(int64_t now, int interval_s, int quiet_start, int quiet_end) {
  if (now <= 0)
    return interval_s * 1000u;
  int64_t local = now + cache.utc_offset;
  int64_t next = (local / interval_s + 1) * interval_s;
  if (quiet_start != quiet_end) {
    int h = (int) ((next % 86400) / 3600);
    bool quiet = quiet_start < quiet_end ? (h >= quiet_start && h < quiet_end) : (h >= quiet_start || h < quiet_end);
    if (quiet) {
      int64_t day = next - next % 86400;
      int64_t end = day + quiet_end * 3600;
      if (end <= next)
        end += 86400;
      next = end;
    }
  }
  return (uint32_t) ((next - local) * 1000 + 2000);  // +2 s so we land just after the boundary
}

// Ordered-dither fill to fake gray on a 1-bit panel. level: 1=light (12%), 2=25%, 3=50%.
inline void dither(Display &it, int x, int y, int w, int h, int level) {
  for (int yy = y; yy < y + h; yy++) {
    for (int xx = x; xx < x + w; xx++) {
      bool on;
      switch (level) {
        case 1:
          on = (xx % 4 == 0) && (yy % 2 == 0) && ((xx / 4 + yy / 2) % 2 == 0);
          break;
        case 2:
          on = (xx % 2 == 0) && (yy % 2 == 0);
          break;
        default:
          on = ((xx + yy) % 2) == 0;
          break;
      }
      if (on)
        it.draw_pixel_at(xx, yy, BLACK);
    }
  }
}

inline void thick_line(Display &it, int x1, int y1, int x2, int y2) {
  for (int d = -1; d <= 1; d++)
    it.line(x1, y1 + d, x2, y2 + d, BLACK);
}

inline void hline_dotted(Display &it, int x, int y, int w) {
  for (int i = 0; i < w; i += 4)
    it.draw_pixel_at(x + i, y, BLACK);
}

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------
struct Fonts {
  BaseFont *huge;   // current temperature, digits only
  BaseFont *large;  // section values
  BaseFont *medium;
  BaseFont *small;
  BaseFont *icon_xl;  // current condition icon
  BaseFont *icon_l;   // daily icons
  BaseFont *icon_s;   // inline icons
};

struct Status {
  const char *location;
  bool de;          // German labels
  bool fahrenheit;  // affects unit labels only; values already arrive in the right unit
  int64_t now;      // unix time, 0 if unknown
  float indoor_t;   // NAN if unavailable
  float indoor_h;
  float vbat;       // NAN if unavailable
  bool charging;
  bool usb;
  bool fetch_ok;    // this wake's fetch succeeded
};

inline void fmt_temp(char *buf, size_t n, float v) {
  if (std::isnan(v))
    snprintf(buf, n, "--");
  else
    snprintf(buf, n, "%.0f°", v);
}

inline void draw_header(Display &it, const Fonts &f, const Status &s) {
  const int32_t off = cache.utc_offset;
  char buf[96];
  int64_t t = s.now ? s.now : cache.fetched;
  if (t) {
    struct tm lt = local_tm(t, off);
    if (s.de)
      snprintf(buf, sizeof(buf), "%s, %d. %s", weekday(lt.tm_wday, true, true), lt.tm_mday, month(lt.tm_mon, true));
    else
      snprintf(buf, sizeof(buf), "%s, %s %d", weekday(lt.tm_wday, false, true), month(lt.tm_mon, false), lt.tm_mday);
    it.print(16, 8, f.medium, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
  }
  it.print(W / 2, 8, f.medium, BLACK, TextAlign::TOP_CENTER, s.location, WHITE);

  // right side: status icons + update time + battery
  int x = W - 16;
  int pct = battery_percent(s.vbat);
  if (pct >= 0) {
    snprintf(buf, sizeof(buf), "%d%%", pct);
    it.print(x, 10, f.small, BLACK, TextAlign::TOP_RIGHT, buf, WHITE);
    int x1, y1, w, h;
    it.get_text_bounds(x, 10, buf, f.small, TextAlign::TOP_RIGHT, &x1, &y1, &w, &h);
    x = x1 - 6;
    // battery glyph drawn with primitives (works with any font)
    int bx = x - 30, by = 12;
    it.rectangle(bx, by, 26, 14, BLACK);
    it.filled_rectangle(bx + 26, by + 4, 3, 6, BLACK);
    int fill = (22 * pct) / 100;
    if (fill > 0)
      it.filled_rectangle(bx + 2, by + 2, fill, 10, BLACK);
    x = bx - 8;
  }
  if (s.charging) {
    it.print(x, 6, f.icon_s, BLACK, TextAlign::TOP_RIGHT, u8(icon::BATTERY_CHARGING).c_str(), WHITE);
    x -= 30;
  }
  if (!s.fetch_ok) {
    it.print(x, 6, f.icon_s, BLACK, TextAlign::TOP_RIGHT, u8(icon::WIFI_OFF).c_str(), WHITE);
    x -= 30;
  }
  if (cache.fetched) {
    struct tm lt = local_tm(cache.fetched, off);
    snprintf(buf, sizeof(buf), "%02d:%02d", lt.tm_hour, lt.tm_min);
    it.print(x, 10, f.small, BLACK, TextAlign::TOP_RIGHT, buf, WHITE);
  }
  it.horizontal_line(0, 44, W, BLACK);
  it.horizontal_line(0, 45, W, BLACK);
}

inline void draw_current(Display &it, const Fonts &f, const Status &s) {
  char buf[64];
  // condition icon
  it.print(20, 52, f.icon_xl, BLACK, TextAlign::TOP_LEFT, u8(code_icon(cache.code, cache.is_day)).c_str(), WHITE);
  // big temperature
  fmt_temp(buf, sizeof(buf), cache.temp);
  it.print(330, 50, f.huge, BLACK, TextAlign::TOP_CENTER, buf, WHITE);
  // description + details
  it.print(190, 172, f.medium, BLACK, TextAlign::TOP_LEFT, code_text(cache.code, s.de), WHITE);
  char feels[16];
  fmt_temp(feels, sizeof(feels), cache.feels);
  snprintf(buf, sizeof(buf), "%s %s", s.de ? "Gefühlt" : "Feels", feels);
  it.print(190, 204, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);

  it.print(24, 196, f.icon_s, BLACK, TextAlign::TOP_LEFT, u8(icon::WIND).c_str(), WHITE);
  snprintf(buf, sizeof(buf), "%.0f %s", cache.wind, s.fahrenheit ? "mph" : "km/h");
  it.print(56, 200, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
  it.print(24, 226, f.icon_s, BLACK, TextAlign::TOP_LEFT, u8(icon::WATER).c_str(), WHITE);
  snprintf(buf, sizeof(buf), "%.0f%%", cache.humidity);
  it.print(56, 230, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
}

inline void draw_side(Display &it, const Fonts &f, const Status &s) {
  const int x0 = 500;
  char buf[48], a[16], b[16];
  it.vertical_line(x0 - 20, 60, 190, BLACK);

  if (std::isnan(s.indoor_t)) {
    // no indoor sensor on this hardware: show tomorrow at a glance instead
    it.print(x0, 58, f.icon_l, BLACK, TextAlign::TOP_LEFT, u8(code_icon(cache.d_code[1], true)).c_str(), WHITE);
    fmt_temp(a, sizeof(a), cache.d_max[1]);
    fmt_temp(b, sizeof(b), cache.d_min[1]);
    snprintf(buf, sizeof(buf), "%s / %s", a, b);
    it.print(x0 + 66, 56, f.large, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
    it.print(x0 + 68, 104, f.small, BLACK, TextAlign::TOP_LEFT, s.de ? "Morgen" : "Tomorrow", WHITE);
  } else {
    // indoor
    it.print(x0, 58, f.icon_l, BLACK, TextAlign::TOP_LEFT, u8(icon::HOME_THERMO).c_str(), WHITE);
    snprintf(buf, sizeof(buf), "%.1f°", s.indoor_t);
    it.print(x0 + 66, 56, f.large, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
    if (!std::isnan(s.indoor_h)) {
      snprintf(buf, sizeof(buf), "%.0f%% %s", s.indoor_h, s.de ? "Luftfeuchte" : "humidity");
      it.print(x0 + 68, 104, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
    }
  }

  hline_dotted(it, x0, 136, W - x0 - 20);

  // today hi / lo / rain
  fmt_temp(a, sizeof(a), cache.d_max[0]);
  fmt_temp(b, sizeof(b), cache.d_min[0]);
  snprintf(buf, sizeof(buf), "%s / %s", a, b);
  it.print(x0, 146, f.medium, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
  it.print(x0 + 170, 144, f.icon_s, BLACK, TextAlign::TOP_LEFT, u8(icon::UMBRELLA).c_str(), WHITE);
  snprintf(buf, sizeof(buf), "%d%%", cache.d_pop[0]);
  it.print(x0 + 200, 148, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);

  // sunrise / sunset
  if (cache.sunrise) {
    struct tm r = local_tm(cache.sunrise, cache.utc_offset), st = local_tm(cache.sunset, cache.utc_offset);
    it.print(x0, 188, f.icon_s, BLACK, TextAlign::TOP_LEFT, u8(icon::SUNRISE).c_str(), WHITE);
    snprintf(buf, sizeof(buf), "%02d:%02d", r.tm_hour, r.tm_min);
    it.print(x0 + 32, 192, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
    it.print(x0 + 130, 188, f.icon_s, BLACK, TextAlign::TOP_LEFT, u8(icon::SUNSET).c_str(), WHITE);
    snprintf(buf, sizeof(buf), "%02d:%02d", st.tm_hour, st.tm_min);
    it.print(x0 + 162, 192, f.small, BLACK, TextAlign::TOP_LEFT, buf, WHITE);
  }
}

// 24 h temperature curve with precipitation-probability bars.
inline void draw_hourly(Display &it, const Fonts &f, const Status &s) {
  const int gx = 56, gy = 268, gw = W - gx - 24, gh = 80;
  it.horizontal_line(0, 258, W, BLACK);

  float lo = 1e9, hi = -1e9;
  for (int i = 0; i < HOURS; i++) {
    if (std::isnan(cache.h_temp[i]))
      continue;
    lo = std::min(lo, cache.h_temp[i]);
    hi = std::max(hi, cache.h_temp[i]);
  }
  if (lo > hi)
    return;
  float lo_r = floorf(lo) - 1, hi_r = ceilf(hi) + 1;
  auto ty = [&](float t) { return gy + gh - (int) lroundf((t - lo_r) / (hi_r - lo_r) * gh); };
  const float step = (float) gw / (HOURS - 1);

  // rain bars (dithered gray, full height = 100 %)
  const int bw = (int) step - 4;
  for (int i = 0; i < HOURS; i++) {
    int bh = cache.h_pop[i] * gh / 100;
    if (bh <= 0)
      continue;
    int bx = gx + (int) lroundf(i * step) - bw / 2;
    dither(it, bx, gy + gh - bh, bw, bh, 1);
    it.rectangle(bx, gy + gh - bh, bw, bh, BLACK);
  }

  // axes + labels
  char buf[16];
  it.horizontal_line(gx, gy + gh, gw, BLACK);
  snprintf(buf, sizeof(buf), "%.0f°", hi_r);
  it.print(gx - 8, gy, f.small, BLACK, TextAlign::CENTER_RIGHT, buf, WHITE);
  snprintf(buf, sizeof(buf), "%.0f°", lo_r);
  it.print(gx - 8, gy + gh - 8, f.small, BLACK, TextAlign::CENTER_RIGHT, buf, WHITE);
  hline_dotted(it, gx, gy, gw);

  // temperature curve: halo pass first, then the black line on top
  for (int pass = 0; pass < 2; pass++) {
    for (int i = 1; i < HOURS; i++) {
      if (std::isnan(cache.h_temp[i - 1]) || std::isnan(cache.h_temp[i]))
        continue;
      int x1 = gx + (int) lroundf((i - 1) * step), x2 = gx + (int) lroundf(i * step);
      int y1 = ty(cache.h_temp[i - 1]), y2 = ty(cache.h_temp[i]);
      if (pass == 0) {
        for (int d = -3; d <= 3; d++)
          it.line(x1, y1 + d, x2, y2 + d, WHITE);
      } else {
        thick_line(it, x1, y1, x2, y2);
      }
    }
  }

  // hour labels every 3 h, plus min/max markers
  for (int i = 0; i < HOURS; i += 3) {
    struct tm lt = local_tm(cache.hour0 + i * 3600, cache.utc_offset);
    int x = gx + (int) lroundf(i * step);
    it.vertical_line(x, gy + gh, 4, BLACK);
    snprintf(buf, sizeof(buf), "%02d", lt.tm_hour);
    it.print(x, gy + gh + 6, f.small, BLACK, TextAlign::TOP_CENTER, buf, WHITE);
  }
}

inline void draw_daily(Display &it, const Fonts &f, const Status &s) {
  const int y0 = 378, colw = W / 5;
  it.horizontal_line(0, y0 - 6, W, BLACK);
  char a[16], b[16], buf[40];
  for (int i = 1; i < DAYS; i++) {
    int cx = (i - 1) * colw + colw / 2;
    if (i > 1)
      it.vertical_line((i - 1) * colw, y0 + 4, H - y0 - 12, BLACK);
    struct tm lt = local_tm(cache.d_time[i], cache.utc_offset);
    it.print(cx, y0, f.small, BLACK, TextAlign::TOP_CENTER, weekday(lt.tm_wday, s.de), WHITE);
    it.print(cx - 28, y0 + 22, f.icon_l, BLACK, TextAlign::TOP_CENTER, u8(code_icon(cache.d_code[i])).c_str(), WHITE);
    fmt_temp(a, sizeof(a), cache.d_max[i]);
    fmt_temp(b, sizeof(b), cache.d_min[i]);
    it.print(cx + 10, y0 + 28, f.medium, BLACK, TextAlign::TOP_LEFT, a, WHITE);
    it.print(cx + 10, y0 + 58, f.small, BLACK, TextAlign::TOP_LEFT, b, WHITE);
    if (cache.d_pop[i] > 0) {
      snprintf(buf, sizeof(buf), "%d%%", cache.d_pop[i]);
      it.print(cx - 28, y0 + 76, f.small, BLACK, TextAlign::TOP_CENTER, buf, WHITE);
    }
  }
}

inline void draw_message(Display &it, const Fonts &f, uint32_t ic, const char *line1, const char *line2) {
  it.print(W / 2, 110, f.icon_xl, BLACK, TextAlign::TOP_CENTER, u8(ic).c_str(), WHITE);
  it.print(W / 2, 270, f.large, BLACK, TextAlign::TOP_CENTER, line1, WHITE);
  it.print(W / 2, 330, f.medium, BLACK, TextAlign::TOP_CENTER, line2, WHITE);
}

// Entry point used by the display lambda.
inline void render(Display &it, const Fonts &f, const Status &s, bool low_battery) {
  it.fill(WHITE);
  if (low_battery) {
    draw_message(it, f, icon::BATTERY_ALERT, s.de ? "Bitte aufladen" : "Please charge",
                 s.de ? "Akku leer – USB-C anschließen" : "Battery empty – connect USB-C");
    return;
  }
  if (!have_data()) {
    draw_message(it, f, icon::WIFI_OFF, s.de ? "Keine Wetterdaten" : "No weather data",
                 s.de ? "WLAN prüfen, Taste drücken" : "Check Wi-Fi, then press the button");
    draw_header(it, f, s);
    return;
  }
  draw_header(it, f, s);
  draw_current(it, f, s);
  draw_side(it, f, s);
  draw_hourly(it, f, s);
  draw_daily(it, f, s);
}

}  // namespace wf
