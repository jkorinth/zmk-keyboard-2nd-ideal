#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/init.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/devicetree.h>

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

static const struct i2c_dt_spec _pca = I2C_DT_SPEC_GET(DT_NODELABEL(pca9555));

static struct k_work_delayable _pca_init_work;

static void scnd_ideal_pca_init(struct k_work *work) {
	ARG_UNUSED(work);

	// apply inversion to all channels
	static uint8_t buf[] = { 0x04, 0xff, 0xff };
	LOG_WRN("[%s] setting inversion register", __func__);
	int ret = i2c_write_dt(&_pca, buf, sizeof(buf));

	if (ret) {
		LOG_ERR("[%s] could not write inversion registers: %d", __func__, ret);
	} else {
		buf[0] = 0xaf; buf[1] = 0xfe;
		ret = i2c_read_dt(&_pca, buf, 2);
		if (ret) {
			LOG_ERR("[%s] could not read inversion registers: %d", __func__, ret);
		} else {
			LOG_INF("[%s] read values: 0x%02x %02x", __func__, buf[0], buf[1]);
		}
	}
	LOG_DBG("[%s] preconfig: %d\n", __func__, ret);
}

static int scnd_ideal_init(void)
{
	if (!device_is_ready(_pca.bus)) {
		return -ENODEV;
	}

	k_work_init_delayable(&_pca_init_work, scnd_ideal_pca_init);
	k_work_schedule(&_pca_init_work, K_MSEC(2000));

	return 0;
}

SYS_INIT(scnd_ideal_init, APPLICATION, CONFIG_APPLICATION_INIT_PRIORITY);
