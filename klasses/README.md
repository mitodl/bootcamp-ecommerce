## How to create a new Bootcamp or Bootcamp Run 

The Bootcamp team will contact Engineering about creating new Bootcamps and Bootcamp runs. They are responsible for 
creating any necessary CMS pages, but we must set up the necessary records in the django admin. 

1. If you don’t have a Bootcamp yet, create one at /admin/klasses/bootcamp/add/ The only field you need is the Title 
of the bootcamp. Don’t check the legacy box. 

2. You can create a Bootcamp run in on the same django admin page, or you can go to /admiin/klasses/bootcamprun/add. 
You will need to fill in the following fields:

   - **Bootcamp ID** the id of the Bootcamp
   - **Run Key** a unique integer, which is used as a primary key. The easiest thing to do is increment the **Run 
     Key** of the last `bootcamprun`
   - **novo_ed_stuff** the significant portion of the NovoEd URL for the online portion of the bootcamp. 
     
   All other fields are legacy and need not be filled in. 
   
3. Create an **Installment** with the payment amount and deadline. 

   _How?_
   
4. If you created a new Bootcamp, you will also need to create new Application Steps. If you already have 
Application Steps you can reu-use them 

   _Instructions TBD_
   

5. Create new Bootcamp Run Application Step(s) at /admin/applications/bootcamprunapplicationstep/add/

   - **Application Step** (Foreign Key)
   - **Bootcamp Run** (Foreign Key)
   - **Due Date** (and time) 

6. Create a new video interview job at admin/jobma/job/add 

   _Instructions TBD_


## How to Test a new Bootcamp Run 


1. Go to/applications/

2. Click Select Bootcamp. 
   
   - Does the new bootcamp appear in the dropdown?

3. Select the new Bootcamp Run.

   - Does the new Bootcamp Run appear on your application dashboard?

4. Expand the Bootcamp application steps

   - Are all the right steps there?
   - Do the steps have the right deadlines?

5. Update your profile, if necessary

6. Upload and/or add a resume link

7. Click through to the vide interview site and confirm the link works. 

8. As an admin, go to /review and admit yourself

9. As the bootcamper again, click through to make a payment. 

   Note that the Cybersource integration will only work on the RC server and in production. On the RC server, you 
   can use a test credit card, but PayPal testing requires a real credit card or bank account. In production, you’ll 
   have to test with a real credit card, and request a refund. 
