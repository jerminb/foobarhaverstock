package com.e.foobar

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.GestureDetector
import android.view.Menu
import android.view.MenuItem
import android.view.MotionEvent
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GestureDetectorCompat
import com.e.foobar.databinding.ActivityMainBinding
import kotlinx.serialization.json.Json
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter


private const val DEBUG_TAG = "Gestures"

class MainActivity : AppCompatActivity() {
    private lateinit var mDetector: GestureDetectorCompat
    private val viewModel: FooBarViewModel by viewModels()
    private lateinit var binding: ActivityMainBinding
    var mIsScrolling: Boolean = false
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setViewBinding()

        binding.mailFab.setOnClickListener { view ->
            val current = LocalDateTime.now()

            val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")
            val formatted = current.format(formatter)
            val json = Json.encodeToString(FooBarModel.serializer(), viewModel.model)
            /*ACTION_SEND action to launch an email client installed on your Android device.*/
            val mIntent = Intent(Intent.ACTION_SEND)
            /*To send an email you need to specify mailto: as URI using setData() method
            and data type will be to text/plain using setType() method*/
            mIntent.data = Uri.parse("mailto:")
            mIntent.type = "text/plain"
            // put recipient email in intent
            /* recipient is put as array because you may wanna send email to multiple emails
               so enter comma(,) separated emails, it will be stored in array*/
            mIntent.putExtra(Intent.EXTRA_EMAIL, arrayOf("jerminb@yahoo.com"))
            //put the Subject in the intent
            mIntent.putExtra(Intent.EXTRA_SUBJECT, "foobar-$formatted")
            //put the message in the intent
            mIntent.putExtra(Intent.EXTRA_TEXT, json)


            try {
                //start email intent
                startActivity(Intent.createChooser(mIntent, "Choose Email Client..."))
            }
            catch (e: Exception){
                //if any thing goes wrong for example no email client application or any exception
                //get and show exception message
                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
            }
        }

        // Instantiate the gesture detector with the
        // application context and an implementation of
        // GestureDetector.OnGestureListener
        mDetector = GestureDetectorCompat(this, GestureListenerDelegate(this, viewModel))
        setSupportActionBar(binding.toolbar);
        setContentView(binding.root)
    }

    override fun onOptionsItemSelected(item: MenuItem) = when (item.itemId) {
        R.id.action_settings -> {
            // User chose the "Settings" item, show the app settings UI...
            true
        }

        R.id.action_refresh -> {
            viewModel.resetPlay()
            setViewBinding()
            true
        }

        else -> {
            // If we got here, the user's action was not recognized.
            // Invoke the superclass to handle it.
            super.onOptionsItemSelected(item)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        mDetector.onTouchEvent(event)
        return super.onTouchEvent(event)
    }

    // Menu icons are inflated just as they were with actionbar
    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    fun setViewBinding(){
        binding.txtPasses.text = viewModel.currentPlayPasses.toString()
        binding.txtCarries.text = viewModel.currentPlayCarries.toString()
        binding.txtCrosses.text = viewModel.currentPlayCrosses.toString()
        binding.txtShots.text = viewModel.currentPlayShots.toString()
        binding.txtPlays.text = viewModel.playsLenght.toString()
    }

    private class GestureListenerDelegate(val activity: MainActivity, val viewModel: FooBarViewModel) : GestureDetector.SimpleOnGestureListener() {
        private fun displayToast(action: PlayAction){
            val toast = Toast(this.activity)
            val view = ImageView(this.activity)
            when(action){
                PlayAction.PASS -> view.setImageResource(R.drawable.fb_pass)
                PlayAction.CARRY -> view.setImageResource(R.drawable.fb_carry)
                PlayAction.CROSS -> view.setImageResource(R.drawable.fb_long_ball)
                PlayAction.SHOT -> view.setImageResource(R.drawable.fb_shot)
            }
            toast.setView(view)
            toast.show()
        }
        private fun incrementCurrentPlay(action: PlayAction){
            viewModel.incrementCurrentPlay(action)
            activity.setViewBinding()
        }

        /**
         * Given two points in the plane p1=(x1, x2) and p2=(y1, y1), this method
         * returns the direction that an arrow pointing from p1 to p2 would have.
         * @param x1 the x position of the first point
         * @param y1 the y position of the first point
         * @param x2 the x position of the second point
         * @param y2 the y position of the second point
         * @return the direction
         */
        fun getDirection(x1: Float, y1: Float, x2: Float, y2: Float): Direction? {
            val angle = getAngle(x1, y1, x2, y2)
            return Direction.fromAngle(angle)
        }

        /**
         *
         * Finds the angle between two points in the plane (x1,y1) and (x2, y2)
         * The angle is measured with 0/360 being the X-axis to the right, angles
         * increase counter clockwise.
         *
         * @param x1 the x position of the first point
         * @param y1 the y position of the first point
         * @param x2 the x position of the second point
         * @param y2 the y position of the second point
         * @return the angle between two points
         */
        private fun getAngle(x1: Float, y1: Float, x2: Float, y2: Float): Double {
            val rad = Math.atan2((y1 - y2).toDouble(), (x2 - x1).toDouble()) + Math.PI
            return (rad * 180 / Math.PI + 180) % 360
        }

        override fun onDoubleTap(event: MotionEvent): Boolean {
            displayToast(PlayAction.SHOT)
            incrementCurrentPlay(PlayAction.SHOT)
            return true
        }

        override fun onSingleTapConfirmed(event: MotionEvent): Boolean {
            displayToast(PlayAction.PASS)
            incrementCurrentPlay(PlayAction.PASS)
            return true
        }

        override fun onLongPress(event: MotionEvent) {
            displayToast(PlayAction.CROSS)
            incrementCurrentPlay(PlayAction.CROSS)
        }

        override fun onScroll(
            event1: MotionEvent?,
            event2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            Log.d(DEBUG_TAG, "onScroll: $event1 $event2")
            activity.mIsScrolling = true
            return true
        }

        override fun onFling(
            event1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            Log.d(DEBUG_TAG, "onFling: $event1")
            val x1: Float = event1!!.getX()
            val y1: Float = event1!!.getY()

            val x2 = e2.x
            val y2 = e2.y
            val direction = getDirection(x1, y1, x2, y2)
            if ((direction == Direction.up) || (direction == Direction.down)) {
                displayToast(PlayAction.CARRY)
                incrementCurrentPlay(PlayAction.CARRY)
            } else {
                viewModel.getNextPlay()
                activity.setViewBinding()
            }
            return true
        }
    }
}