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

	printk("deferred task is running now!\n");
	LOG_ERR("error message from deferred task");

	// apply inversion to all channels
	static uint8_t buf[] = { 0x04, 0xff, 0xff };
	//static uint8_t buf[] = { 0x04, 0x00, 0x00 };
	LOG_WRN("[pca9555] setting inversion register to invert\n");
	int ret = i2c_write_dt(&_pca, buf, sizeof(buf));

	if (ret) {
		LOG_ERR("[pca9555] could not write inversion registers: %d\n", ret);
	} else {
		buf[0] = 0xaf; buf[1] = 0xfe;
		ret = i2c_read_dt(&_pca, buf, 2);
		if (ret) {
			LOG_ERR("[pca9555] could not read inversion registers: %d\n", ret);
		} else {
			LOG_WRN("[pca9555] read values: 0x%02x %02x\n", buf[0], buf[1]);
		}
	}
	LOG_ERR("[pca9555] preconfig: %d\n", ret);
}

static int scnd_ideal_init(void)
{
	if (!device_is_ready(_pca.bus)) {
		return -ENODEV;
	}

	k_work_init_delayable(&_pca_init_work, scnd_ideal_pca_init);
	k_work_schedule(&_pca_init_work, K_MSEC(1000));

	return 0;
}

SYS_INIT(scnd_ideal_init, APPLICATION, CONFIG_APPLICATION_INIT_PRIORITY);
